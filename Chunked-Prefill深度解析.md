# Chunked Prefill：让大模型推理从"一核有难"变为"全员平滑"的调度艺术

> 本文从原理、硬件、实战三个维度，深度拆解 LLM 推理中最"杀手级"的优化技术——Chunked Prefill。

---

## 一、一个真实场景：为什么你的推理服务会突然"卡死"？

假设你部署了一个大模型推理服务，系统里有 50 个用户正在流畅地聊天（每人每 30ms 吐出一个字），此时突然来了一个用户，发了一段 **10 万 Token 的超长文本**需要分析。

接下来发生了什么？

**传统模式下**，GPU 不得不一次性处理这 10 万 Token 的 Prefill（预填充）。在这个长达 2~5 秒的计算过程中，GPU 的算力被完全占满——那 50 个正在聊天的用户，他们的 Decode（逐字生成）任务被迫排队等待，表现为**对话框突然毫无征兆地卡死几秒钟**。

这就是 LLM 推理中经典的"一核有难，多核围观"——更准确地说，是"一个长文本请求，拖垮所有并发用户"。

而 Chunked Prefill，正是为了解决这个问题而生的。

---

## 二、根本矛盾：Prefill 与 Decode 的"资源互斥"

要理解 Chunked Prefill 为什么厉害，首先要理解 LLM 推理中两个阶段的本质差异：

| 阶段 | 工作内容 | GPU 负载特征 | 瓶颈 |
|------|---------|-------------|------|
| **Prefill（预填充）** | 一次性处理全部输入 Prompt，生成 KV Cache | 计算密集型（Compute-Bound） | Tensor Cores 算力 |
| **Decode（解码）** | 每次生成 1 个 Token，逐字输出 | 访存密集型（Memory-Bound） | HBM 显存带宽 |

**Prefill 阶段**：处理的是一个大矩阵乘大矩阵（GEMM）运算，GPU 的计算单元（Tensor Cores）被彻底喂饱，算力利用率极高。

**Decode 阶段**：退化为矩阵乘向量（GEMV），每生成 1 个 Token 就要把几十 GB 的模型权重从 HBM 显存重新搬运到计算单元。计算本身不到 1 微秒，但搬运数据需要几毫秒——GPU 的计算单元大量时间处于"空转等数据"的状态。

如果使用传统"全量 Prefill"，这两个阶段是**互斥**的：Prefill 独占 GPU 时，Decode 被迫停工；如果为了照顾 Decode 而排队，长文本请求的 TTFT（首字延迟）又会急剧上升。

---

## 三、Chunked Prefill 的核心思想："打散重排"

Chunked Prefill 的解法极其优雅：**把不可中断的重型任务，改造为可中断的轻量级序列**。

具体来说，它将超长 Prompt 切分成多个固定大小的"小块"（Chunk，例如 4096 个 Token）。推理过程中，模型处理完一个 Chunk 后，**立即切回 Decode 模式处理一轮 Token 生成**，然后再继续下一个 Chunk 的处理。

用一张图来理解调度节奏的变化：

```
传统 Full Prefill：
|████████████████ 长文本 Prefill（独占 2 秒）████████████████| → 开始 Decode
   ↑ 期间其他 50 个用户的 Decode 全部卡死

Chunked Prefill：
|C1 + 50 人 Decode| → |C2 + 50 人 Decode| → |C3 + 50 人 Decode| → |C4 + 50 人 Decode| → 开始 Decode
   ↑ 每次只算一小段，算完立即帮其他人吐一个字，循环往复
```

**结果对比：**
- **长文本用户**：TTFT 从 2.0 秒变为 2.2 秒（多等了 0.2 秒）
- **其他 50 个用户**：从"卡死 2 秒"变为"完全无感知"

这就是 Chunked Prefill 的核心哲学：**牺牲局部的极速，换取全局的稳定**。

---

## 四、关键问题：分块处理会丢失信息吗？

这是很多人的第一反应——Prompt 被切碎了，模型的理解会不会出问题？

答案是：**不会，100% 无损**。

原因在于 KV Cache 机制的数学本质。Transformer 的 Self-Attention 公式决定了：

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

当模型处理第 n 个 Chunk 时，它会读取前 n-1 个 Chunk 已存入显存的 Key 和 Value 矩阵，并与之拼接计算：

处理 C₁：生成 K_{C1}、V_{C1} 存入显存

处理 C₂：Attention(Q_{C2}, [K_{C1}, K_{C2}], [V_{C1}, V_{C2}])

处理 C₃：Attention(Q_{C3}, [K_{C1}, K_{C2}, K_{C3}], [V_{C1}, V_{C2}, V_{C3}])

**最终显存中的 KV Cache，与一次性完整 Prefill 的结果是比特级完全一致的。**

一个直观类比：你要计算 `1+2+3+4+5+6=21`。一次性算完，还是先算 `1+2+3=6`，存下中间结果，再算 `6+4+5+6=21`——最终结果相同。KV Cache 就是存在显存里的"中间和"。

> **注意**：Chunked Prefill 不是"滑动窗口"或"截断"——它完整保留了所有上下文信息，只是把计算动作拆散了。

---

## 五、硬件层面的"神仙操作"：同时压榨算力与带宽

理解了上述调度逻辑后，我们再深入到 GPU 硬件层面，看看 Chunked Prefill 为什么能实现资源利用率的质变。

### GPU 的存储层级

- **HBM（显存）**：容量大，带宽有限。存放模型权重和 KV Cache。
- **SRAM（片上缓存）**：容量极小（几 MB），但带宽极高（比 HBM 快 1~2 个数量级）。Tensor Cores 计算时，数据必须先搬到这里。

### Chunked Prefill 的"搭便车"策略

Decode 阶段，GPU 反正都要把几十 GB 的模型权重从 HBM 搬运到 SRAM 一次——这期间计算单元在"空转等数据"。既然权重已经搬进来了，为什么不**顺手**让一个 Chunked Prefill（比如 512 个 Token）也和这些权重做一次矩阵乘法呢？

这就形成了一个**异构混合 Batch**：

```
同一个 Batch 里：
├── Chunked Prefill（512 tokens）：填满 Tensor Cores 的算力 ← 计算密集型
└── 多个 Decode 请求：消耗 HBM 带宽搬运权重        ← 访存密集型
```

**在一次 GPU Kernel 调用中，把 Tensor Cores 和 HBM 带宽同时压榨到物理极限。**

这与 CPU 指令流水线的理念完全同源——都是通过"时分复用"和"任务交错"来消灭硬件气泡。

---

## 六、实战配置：TP2 + FlashInfer + Chunked Prefill = 性能铁三角

以下是一套部署 Qwen3.6-35B 的生产级配置：

```bash
--tp-size 2                    # 张量并行，两张卡池化 96GB 显存
--enable-flashinfer            # 激进优化的 Attention 后端
--chunked-prefill-size 4096    # 每次 Prefill 4096 个 Token
--context-length 131072        # 支持 128K 超长上下文
--max-running-requests 4       # 最大同时计算 4 个请求
--kv-cache-dtype fp8_e5m2      # KV Cache 使用 FP8 量化
```

**实测数据（128K 上下文、4 并发）：**
- TTFT（首字延迟）：**1.47 秒**
- 输出吞吐：**137.2 tok/s**
- 有效显存带宽利用率：约 **70%**（在生产环境中属于极高水平）

### 各参数的角色

| 参数 | 角色 | 为什么关键 |
|------|------|-----------|
| `--tp-size 2` | 物理基础 | 总显存 96GB，扣除 17.5GB 权重，剩余空间刚好容纳 4 个 128K 并发请求的 KV Cache；同时带宽翻倍 |
| `--enable-flashinfer` | 底层效率 | 针对 Ada Lovelace 架构（`TORCH_CUDA_ARCH_LIST="8.9"`）极致优化 Attention 算子，大幅减少 SRAM-HBM 数据搬运 |
| `--chunked-prefill-size 4096` | 调度节拍 | 4096 是"甜点"值：够大，能填满 Tensor Cores；够小，算完立即切去 Decode（几十到上百毫秒），保证并发平滑 |

---

## 七、一次线上 Crash 的根因分析

在压测过程中，出现过一次服务崩溃。日志的关键信息：

```
sampling_params={'temperature': 0.0, 'max_new_tokens': 50000, ...}

RuntimeError: Runtime check failed at 
  per_token_group_quant_8bit.cuh:203: CUDA error: unknown error
```

**根因**：客户端传入了 `max_new_tokens: 50000` 的"毒药请求"。50,000 次自回归生成导致：
1. Paged KV Cache 在 HBM 中疯狂申请数万 Block，触发显存碎片化
2. FP8 MoE 底层 CUDA Kernel 在处理极端序列长度时，索引偏移量可能溢出，访问了非法显存地址
3. TP=2 模式下，一张卡崩溃 -> NCCL 通信超时 -> 全盘死锁

**修复方案**：在客户端层面对不同场景设置合理的 `max_tokens` 上限：

```json
// 纯解释场景
{
    "temperature": 0.1,
    "top_p": 0.95,
    "repetition_penalty": 1.05,
    "max_tokens": 8192
}

// Tool Call 场景
{
    "temperature": 0.0,
    "max_tokens": 4096,
    "chat_template_kwargs": { "enable_thinking": false }
}
```

> 建议在 API 网关层（如 Nginx 或 FastAPI 代理）对 `max_tokens` 做强制校验拦截，从入口杜绝"毒药请求"。

---

## 八、总结：一张表看懂 Chunked Prefill

| 维度 | 传统 Full Prefill | Chunked Prefill |
|------|------------------|-----------------|
| 长文本 TTFT | 很快（独占算力） | 略慢（~10% 额外开销） |
| 并发用户 ITL | 灾难级卡顿（2~5 秒停顿） | 平滑无感知 |
| GPU 算力利用率 | 波峰波谷剧烈 | 削峰填谷，平稳满载 |
| 显存压力 | 瞬间峰值高 | 分步递增，更可控 |
| 适用场景 | 单用户低并发 | 多用户高并发 + 长上下文 |

**一句话总结**：Chunked Prefill 不是让单个请求更快，而是让整个系统在高压下不崩溃。它将 LLM 推理从"看天吃饭"的赌运气调度，进化为"平稳可控"的工程化调度。



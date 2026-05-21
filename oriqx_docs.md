## Quick start guide
Getting Started
Get up and running with the uniqx computing platform. This guide walks you through installation, authentication, and your first job submission.

Prerequisites
Requirement	Version
Python	3.9 or later
pip	Latest recommended
Operating System	Linux, macOS, or Windows (WSL)
Installation
Install the uniqx SDK from PyPI:

Copy
pip install uniqx
Tip

We recommend using a virtual environment: python -m venv .venv && source .venv/bin/activate
Authentication
Connect to the gateway with your endpoint URL. Set UNIQX_API_KEY in your environment or pass it directly.

Copy
import uniqx as ux

# Connect to the gateway (uses UNIQX_API_KEY env var by default)
client = ux.connect("localhost:50050")

# Or connect to the hosted platform
client = ux.connect("app.oriqx.com:50050")
Your First Job
Uniqx uses traced modules to capture computation graphs. Use the @trace decorator to define operations. The platform scores, compiles, and optimizes them automatically before execution.

Copy
import uniqx as ux
import numpy as np

# 1. Define a traced function
@ux.trace
def compute_energy(H, psi, t):
    evolved = ux.expv(H, psi, t, hermitian=True)
    energy = ux.expect(H, evolved)
    return energy

# 2. Create the module with concrete inputs
H = np.array([[0.5, 0.1], [0.1, -0.5]])
psi = np.array([1.0, 0.0, 0.0, 0.0])
t = 0.1
module = compute_energy(H, psi, t)

# 3. Submit to the gateway
job_id = ux.submit(module)

# 4. Get results
result = ux.get(job_id)
print(result)
Preflight Check
Score execution options without running. The gateway returns a ranked list of candidates with predicted time, cost, accuracy, and carbon across the available hardware mix.

Copy
options = ux.preflight(module)
print(options.summary())   # Text table of execution options
options.plot()              # Matplotlib grouped bar chart

# Select a specific option and submit
job_id = ux.submit(module,
    preflight_job_id=options.job_id,
    option_idx=2)  # e.g. pick the 3rd option
Core Concepts
Concept	Description
Module	A traced computation graph built by the @trace decorator from Python functions.
Primitive	A high-level operation (expv, expect, eigs) that is hardware-agnostic. The system selects the best execution model for the job.
Modality	Hardware hint on a primitive: "auto" (default), "cpu", "gpu", "qpu", or "hybrid".
Preflight	Scoring pass that returns ranked execution candidates with predicted time/cost/accuracy/carbon, without running the job.
Execution Option	One candidate execution plan with a label, predicted metrics, and a hardware assignment.
Dialect	Hardware-specific op set: quantum (gates, measurement), gpu (BLAS/LAPACK), tpu (XLA HLO).
Job	A submitted module compiled, optimized, and executed on the gateway.
Result	Buffer-view encoded output parsed into Python arrays by the SDK.
Note

Primitives are not tied to any specific hardware. A single primitive like expv can run on CPU, GPU, QPU, or hybrid combinations. The platform selects the best execution model automatically, or you can choose one explicitly.
uniqx documentation by ORIQX — for the latest updates, visit oriqx.com

## SDK information:
SDK Reference
Complete reference for the uniqx Python SDK.

Tracing API
@trace(fn: Callable, *call_args, name: str | None = None) -> Module
Trace a Python function into an eqxir Module. Call with concrete NumPy arrays. Inside the function, Python arithmetic on TracerValues emits IR ops.

@tracing.to_module(fn: Callable, *, name: str | None = None) -> ModuleFactory
Decorator variant of trace. Converts a function into a reusable module producer.

module.to_text(truncate: bool = False) -> str
Serializes the traced module to its eqxir text representation.

module.to_dot() -> str
Renders the module as a GraphViz DOT string for visualization.

Execution API
uniqx.connect(target: str, api_key: str | None = None) -> Client
Establishes a gRPC connection to the gateway. Returns a client and sets it as the default.

uniqx.submit(module, client=None, preflight_job_id=None, option_idx=None, runtime_inputs=None, backend=None) -> str (job_id)
Submits a traced module for execution. Optionally reuse a prior preflight analysis.

uniqx.get(job_id, client=None, wait=True, poll_interval=0.2, timeout=300.0) -> GetResultResponse
Blocks until the job completes. Returns result with state, payload, execution options, timings, and cost.

uniqx.preflight(module, client=None) -> PreflightResult
Score execution options without running. Returns a ranked list of candidates with predicted time, cost, accuracy, and carbon.

uniqx.get_hardware(client=None) -> HardwareCatalog
Query the gateway for available hardware providers, targets, and capabilities.

PreflightResult
PreflightResult extends list — each element is an execution option dict.

Property / Method	Description
options.job_id	Job ID for round-tripping to submit()
options.recommended	Recommended option (or first)
options.by_label("cpu+gpu")	Find option by label prefix
options.needs_gpu	True if any option uses GPU
options.needs_qpu	True if any option uses QPU
options.summary(actuals=None)	Text table of all options
options.plot(actuals=None)	Matplotlib grouped bar chart
Result Parsing
Function	Description
parse_result(payload, names)	Parse gateway result into dict of named outputs
parse_buffer_view(line)	Parse buffer-view string to (dims, dtype, values)
fmt_vec(v, n, dtype="f64")	Encode 1-D vector as buffer-view string
fmt_mat(m, rows, cols, dtype="f64")	Encode row-major matrix as buffer-view string
fmt_scalar(x, dtype="f64")	Encode scalar as buffer-view string
Arithmetic Operations
Element-wise arithmetic via uniqx.ops.arith. Also available via Python operators on TracerValue: a + b, a - b, a * b, a / b.

Operation	Description
ops.arith.add(a, b)	Element-wise addition
ops.arith.sub(a, b)	Element-wise subtraction
ops.arith.mul(a, b)	Element-wise multiplication
ops.arith.div(a, b)	Element-wise division
ops.arith.neg(a)	Unary negation
ops.arith.abs(a)	Absolute value
ops.arith.pow(a, b)	Element-wise exponentiation
ops.arith.rem(a, b)	Element-wise remainder
ops.arith.max(a, b)	Element-wise maximum
ops.arith.min(a, b)	Element-wise minimum
ops.arith.sign(a)	Sign: -1 / 0 / +1
ops.arith.clip(a, lo, hi)	Clamp to [lo, hi]
Transcendental Operations
Via uniqx.ops.trans:

Operation	Description
ops.trans.sin(a)	Sine
ops.trans.cos(a)	Cosine
ops.trans.tan(a)	Tangent
ops.trans.exp(a)	Natural exponential
ops.trans.expm1(a)	exp(x) - 1 (good small-x behavior)
ops.trans.log(a)	Natural logarithm
ops.trans.log1p(a)	log(1 + x) (good small-x behavior)
ops.trans.tanh(a)	Hyperbolic tangent
ops.trans.sqrt(a)	Square root
ops.trans.rsqrt(a)	Reciprocal square root
ops.trans.cbrt(a)	Cubic root
ops.trans.atan2(y, x)	Two-argument arctangent
ops.trans.logistic(a)	Sigmoid: 1 / (1 + exp(-x))
ops.trans.erf(a)	Gauss error function
Linear Algebra
Via uniqx.ops.linalg:

Operation	Description
ops.linalg.matmul(a, b)	Matrix multiplication with batching
ops.linalg.dot(a, b)	Inner product / batched dot
ops.linalg.kron(a, b)	Kronecker product of 2-D tensors
ops.linalg.dft(signal)	Discrete Fourier Transform (returns real, imag)
ops.linalg.embed(op, qubit, n_qubits)	Embed single-qubit operator into full space
ops.linalg.two_body(opA, opB, qa, qb, n)	Embed two-body term at qubits qa, qb
ops.linalg.spectrum_from_fid(fid, t_step)	DFT of FID signal to (freqs_hz, amplitudes)
Shape Operations
Via uniqx.ops.shape:

Operation	Description
ops.shape.transpose(a, perm)	Transpose with permutation
ops.shape.reshape(a, result_type=...)	Reshape tensor
ops.shape.slice(a, start, limit, strides)	Extract contiguous slice
ops.shape.concatenate(*args, axis=...)	Concatenate along axis
ops.shape.diag(a, k=0)	Extract or construct diagonal
ops.shape.eye(n, m=None, k=0)	Identity matrix
ops.shape.trace(a)	Matrix trace
ops.shape.reduce(a, axis=0)	Reduce along axis
Quantum Dialect
Quantum gates and measurement via uniqx.dialects.quantum. Executed through qsim (CPU) or cuQuantum (GPU).

Operation	Description
quantum.h(q)	Hadamard gate
quantum.x(q) / y(q) / z(q)	Pauli X, Y, Z gates
quantum.s(q) / t(q)	S and T phase gates
quantum.rx(theta, q) / ry / rz	Parameterized rotation gates
quantum.cnot(ctrl, tgt)	Controlled-NOT
quantum.cz(ctrl, tgt)	Controlled-Z
quantum.cphase(theta, ctrl, tgt)	Controlled phase
quantum.swap(a, b)	SWAP gate
quantum.measure(q)	Projective measurement
quantum.reset(q)	Reset to |0⟩
quantum.barrier(q)	Optimization barrier
quantum.circuit(n_qubits, n_clbits=0)	Quantum register type
Copy
import uniqx as ux
from uniqx.dialects import quantum

@ux.to_module
def bell(q0, q1):
    q0 = quantum.h(q0)
    q1 = quantum.cnot(q0, q1)
    m0 = quantum.measure(q0)
    m1 = quantum.measure(q1)
    return m0, m1

mod = bell(ux.qubit(), ux.qubit())
GPU Dialect
Vendor-agnostic GPU BLAS/LAPACK ops via uniqx.dialects.gpu. Lowered to cuBLAS/cuSOLVER (NVIDIA) or rocBLAS (AMD) by the gateway.

Operation	Description
gpu.gemm(A, B)	GPU matrix-matrix multiply (GEMM) via cuBLAS
gpu.gemv(A, x)	GPU matrix-vector multiply (GEMV)
gpu.dot(a, b)	GPU dot product
gpu.scal(alpha, x)	GPU scalar-vector multiply: y = alpha * x
gpu.axpy(alpha, x, y)	GPU AXPY: y = alpha * x + y
gpu.syevd(A)	GPU symmetric eigenvalue decomposition via cuSOLVER
gpu.composite(x, attrs=...)	Fused GPU kernel for a traced sub-graph
Copy
import uniqx as ux
from uniqx.dialects import gpu

@ux.to_module
def compute(A, B):
    C = gpu.gemm(A, B)         # GPU matrix multiply
    vals = gpu.syevd(C)        # GPU eigenvalue decomposition
    return vals
TPU Dialect
TPU ops via uniqx.dialects.tpu. Lowered to XLA HLO for execution on Cloud TPU pods. Optimal for large-batch matrix operations and bf16/f32 dtypes.

Operation	Description
tpu.matmul(A, B)	TPU matrix multiply via XLA HLO dot_general (MXU)
tpu.conv(input, kernel, padding="same")	TPU convolution via XLA HLO
tpu.reduce_sum(x, axis=None)	TPU reduction (sum) on vector unit
tpu.all_reduce(x, replica_groups=None)	Cross-replica all-reduce for distributed training
tpu.infeed(x)	Stream data from host to TPU HBM
tpu.outfeed(x)	Stream results from TPU HBM to host
Copy
import uniqx as ux
from uniqx.dialects import tpu

@ux.to_module
def train_step(weights, activations, gradients):
    logits = tpu.matmul(activations, weights)
    grad_update = tpu.all_reduce(gradients)
    return logits, grad_update
Primitives (Hardware-Agnostic)
All primitives are available directly on the ux namespace (import uniqx as ux). Each accepts a modality hint: "auto", "cpu", "gpu", "qpu".

Operation	Description
ux.expv(A, v, t, hermitian=True)	Matrix exponential: exp(tA)v
ux.time_evolve(H, state, t)	Time evolution under Hamiltonian
ux.eigs(op, k=1, which="smallest")	Leading eigenvalues/eigenvectors
ux.expect(op, state, shots=None)	Expectation value ⟨state|op|state⟩
ux.sample(op, state, n_samples=1000)	Sample measurement outcomes
ux.linear_solve(A, b)	Solve Ax = b
ux.apply_linear(op, state)	Apply linear map to state
Control Flow
Operation	Description
ux.cond(pred, true_fn, false_fn, *args)	Conditional branch
ux.while_loop(cond_fn, body_fn, init)	Loop with condition
ux.for_loop(start, stop, body_fn, init)	Counted loop
ux.fori_loop(lo, hi, body_fn, init)	JAX-style loop: body(i, carry)
ux.scan_loop(lo, hi, body_fn, init)	Scan with output collection
Supported Data Types
Type	Description	NumPy
f32	32-bit floating point	np.float32
f64	64-bit floating point (default)	np.float64
complex64	64-bit complex	np.complex64
complex128	128-bit complex	np.complex128
i32	32-bit integer	np.int32
i64	64-bit integer	np.int64
i16 / i8	16-bit / 8-bit integer	np.int16 / np.int8
bool	Boolean	np.bool_
uniqx documentation by ORIQX — for the latest updates, visit oriqx.com


# Pipeline Phases
Every job submitted to the gateway passes through a sequence of phases. Understanding these phases helps you debug failures and optimize performance.

Phase	Input	Output
1. Parse	Runtime input strings	ExecutionConfig (iterations, backend, overrides)
2. Analyze	Computation graph + hardware state	Ranked execution plan
3. Preflight	Execution plan	JSON options (returned early if preflight=True)
4. Introspect	Graph constants	Numerical params (H, M, dim, n_qubits)
5. Lower	Graph + selected option	Hardware-specific lowered graph
6. Translate	Lowered DAG + inputs	Plan with slots, steps, feedback wiring
7. Compile + Execute	Plan	Buffer-view result string

Parse
Scans runtime-input strings for control tags like iterations=256, backend=compiled, and preflight_ref=abc/2. Tags are extracted into the config; everything else is forwarded as data.


Analyze
Scores every operation across the available hardware (CPU, GPU, QPU) on four dimensions: time, cost, accuracy, and carbon. Returns a ranked list of execution options.


Preflight (optional)
If preflight=True, serializes execution options and returns them immediately. No compilation or execution occurs. Resubmit with preflight_ref=<job_id>/<idx> to select a specific option.


Introspect
Extracts numerical parameters from constant nodes: Hamiltonian matrix (h_flat), observable matrix (mx_flat), Hilbert space dimension, qubit count, hermiticity flag, and substep ratio for Taylor propagation stability.


Lower
Replaces high-level primitives (expv, expect, eigs) with hardware-specific subgraphs. Traverses the DAG in topological order. Each hardware variant is explicit — no silent fallthrough from QPU to CPU.


Translate
Converts the lowered graph into an execution plan. Classical blocks run on CPU / GPU; quantum blocks run on the configured QPU backend (qsim or cuquantum). Feedback slots wire iteration outputs back to inputs.


Compile and Execute
Code is compiled to native machine code via LLVM (cached by SHA256). The execution loop runs K iterations with state feedback, collecting one scalar per step. Results are returned as buffer-view strings.

Copy
state = initial_state
for i in 1..K:
    (new_state, scalar) = backend.step(state, params)
    state = new_state
result = [scalar_1, scalar_2, ..., scalar_K]
Job State Machine
Copy
PENDING -> PROCESSING -> GRAPHED -> TRANSLATED -> PRECOMPILE
  -> COMPILING -> POSTCOMPILE -> RUNNING -> RUNNING_FINISHED -> COMPLETED
                                                              -> FAILED
Full pipeline reference: docs.oriqx.com/architecture/pipeline

# Operations Catalog
Low-level IR operations available in the uniqx SDK. These are elementary building blocks that compile directly to hardware instructions. For high-level semantic operations (evolution, measurement, solvers), see the Primitives & Execution tab.


Arithmetic Operations (12 ops)
Operation	Signature	Description
add	add(lhs, rhs)	Element-wise addition
sub	sub(lhs, rhs)	Element-wise subtraction
mul	mul(lhs, rhs)	Element-wise multiplication
div	div(lhs, rhs)	Element-wise division
pow	pow(lhs, rhs)	Element-wise exponentiation
rem	rem(lhs, rhs)	Element-wise remainder
max	max(lhs, rhs)	Element-wise maximum
min	min(lhs, rhs)	Element-wise minimum
neg	neg(a)	Unary negation
abs	abs(a)	Absolute value
sign	sign(a)	Sign function: -1 / 0 / +1
clip	clip(a, lo, hi)	Clamp values to [lo, hi]

Transcendental & Special Functions (14 ops)
Operation	Signature	Description
sin	sin(a)	Sine
cos	cos(a)	Cosine
tan	tan(a)	Tangent
exp	exp(a)	Natural exponential
expm1	expm1(a)	exp(x) - 1 (stable for small x)
log	log(a)	Natural logarithm
log1p	log1p(a)	log(1+x) (stable for small x)
tanh	tanh(a)	Hyperbolic tangent
sqrt	sqrt(a)	Square root
rsqrt	rsqrt(a)	Reciprocal square root
cbrt	cbrt(a)	Cube root
atan2	atan2(y, x)	Two-argument arctangent
logistic	logistic(a)	Sigmoid function
erf	erf(a)	Gauss error function

Linear Algebra (7 ops)
Operation	Signature	Description
dot	dot(a, b)	Inner product / general contraction
matmul	matmul(a, b)	Matrix multiplication with batch dimensions
kron	kron(a, b)	Kronecker product: A⊗B
dft	dft(signal)	Discrete Fourier Transform
embed	embed(op, qubit, n_qubits)	Embed operator into n-qubit space
two_body	two_body(opA, opB, qa, qb, n)	Embed two-body interaction
spectrum_from_fid	spectrum_from_fid(fid, t_step, zero_pad_factor)	FFT the FID signal

Shape & Structural Operations (8 ops)
Operation	Signature	Description
transpose	transpose(a, permutation)	Permute dimensions
reshape	reshape(a, result_type)	Reshape tensor
slice	slice(a, start, limit, strides)	Extract sub-tensor
concatenate	concatenate(*tensors, axis)	Concatenate along axis
diag	diag(a, k=0)	Extract or construct diagonal
eye	eye(n, m, k)	Identity matrix
trace	trace(a, axis1, axis2)	Matrix trace
reduce	reduce(a, axis)	Generic reduction

Bitwise Operations (9 ops)
Operation	Signature	Description
bitwise_not	bitwise_not(a)	Logical NOT
bitwise_and	bitwise_and(a, b)	Bitwise AND
bitwise_or	bitwise_or(a, b)	Bitwise OR
bitwise_xor	bitwise_xor(a, b)	Bitwise XOR
shift_left	shift_left(a, b)	Left shift
shift_right_logical	shift_right_logical(a, b)	Logical right shift
shift_right_arithmetic	shift_right_arithmetic(a, b)	Arithmetic right shift
popcnt	popcnt(a)	Population count
count_leading_zeros	count_leading_zeros(a)	Count leading zeros

Control Flow (4 ops)
Operation	Signature	Description
cond	cond(pred, true_fn, false_fn, *args)	Conditional branch
while_loop	while_loop(init, result_types)	Traced while loop
for_loop	for_loop(start, stop, init, step)	Counted iteration
scan	scan(init, seqs, result_types)	Fold over sequences

Indexing & Tensor Contraction (3 ops)
Operation	Signature	Description
gather	gather(operand, indices, *, axis=0)	Pick rows along an axis using an integer index tensor
scatter_add	scatter_add(operand, indices, updates, *, axis=0)	Accumulate updates into operand at the given indices (combiner=add)
einsum	einsum(subscripts, *operands)	Generalized tensor contraction in Einstein-summation notation

Comparison & Selection (2 ops)
Operation	Signature	Description
compare	compare(lhs, rhs, *, direction)	Elementwise comparison (eq/ne/lt/le/gt/ge) returning a boolean tensor
select	select(pred, on_true, on_false)	Elementwise selection from two tensors based on a boolean predicate

Constants & Structural (4 ops)
Operation	Signature	Description
constant	constant(value, *, dtype=None)	Materialize a literal scalar or tensor in the graph
arg	arg(index, *, dtype, shape)	Reference a graph input by position
tuple	tuple(*xs)	Pack multiple values into a tuple result
composite	composite(name, *xs, **attrs)	Opaque user-defined op that the gateway may lower as a custom_call
Quantum Gate Operations
Quantum dialect ops live alongside classical ops in the IR. The gateway preserves them as eqxir.node in StableHLO and routes them to the configured QPU backend. Use these through uniqx.dialects.quantum.


Single-Qubit Clifford & Phase Gates (6 ops)
Operation	Signature	Description
h	h(q)	Hadamard gate
x	x(q)	Pauli-X (bit-flip)
y	y(q)	Pauli-Y
z	z(q)	Pauli-Z (phase-flip)
s	s(q)	S gate (√Z)
t	t(q)	T gate (√S)

Parameterized Rotations (3 ops)
Operation	Signature	Description
rx	rx(q, theta)	Rotation about the X axis by angle theta
ry	ry(q, theta)	Rotation about the Y axis by angle theta
rz	rz(q, theta)	Rotation about the Z axis by angle theta

Two-Qubit Gates (4 ops)
Operation	Signature	Description
cnot	cnot(ctrl, tgt)	Controlled-X (CNOT) entangling gate
cz	cz(q0, q1)	Controlled-Z
cphase	cphase(q0, q1, theta)	Controlled phase rotation by theta
swap	swap(q0, q1)	Exchange the state of two qubits

Measurement & Circuit Ops (3 ops)
Operation	Signature	Description
reset	reset(q)	Project qubit to |0⟩ (mid-circuit reset)
measure	measure(q, c)	Projective measurement of q into classical bit c
barrier	barrier(*qubits)	Compiler barrier preventing gate reordering across the marker
Note

Looking for high-level primitives like expv, expect, or reduce_sum? See the Primitives & Execution tab for ~40 primitives with detailed algorithm decompositions per execution model. For operator-construction blocks (chemistry/physics/ML/optimization), see the Kernels & Domain Blocks tab.
Hardware Support for Ops
Category	CPU	CPU+GPU	QPU	Notes
Arithmetic (12)	✓	✓	—	Native instructions on all classical targets
Transcendental (14)	✓	✓	—	GPU uses fast-math intrinsics
Linear Algebra (7)	✓	✓	—	GPU uses accelerated BLAS kernels
Shape (8)	✓	✓	—	Zero-cost view operations at compile time
Bitwise (9)	✓	✓	—	Integer-only operations
Control Flow (4)	✓	✓	✓	Structured loops and branches; preserved in StableHLO and quantum circuits
Indexing (3)	✓	✓	—	gather / scatter_add / einsum lower directly to StableHLO
Comparison & Selection (2)	✓	✓	—	Elementwise predicates used in cond/select branches
Constants & Structural (4)	✓	✓	–	Compile-time constants and tuple packing; arg is graph-input only
Quantum Gates (16)	—	—	✓	Preserved as eqxir.node in StableHLO; routed to QPU backend

# Primitives & Execution Models
Primitives are hardware-agnostic high-level operations. Each primitive has multiple algorithm decompositions, one per execution model — the platform's planner picks the decomposition that best fits the job, the operator, and the available hardware. Expand any card below to see the algorithms behind each execution mode.

Note

6 execution models are considered for every primitive: CPU, CPU+GPU, CPU+TPU, CPU+QPU, CPU+GPU+QPU (NISQ), and CPU+GPU+QPU (FTQC). If a primitive cannot be lowered to a particular model, it is marked Not Available.

Evolution Primitives (5)

apply_linear
evolution
apply_linear(op, state, *, modality=None) -> Tensor

Apply a linear operator to a state vector: op|state\u27E9. The fundamental building block for state transformations.


expv
evolution
expv(A, v, t, *, A_is_generator=True, hermitian=False, sparse=False, precision=1e-6, modality=None) -> Tensor

Compute exp(tA)|v\u27E9 \u2014 matrix exponential applied to a vector without forming the full matrix exponential. Core primitive for time evolution and dynamics.


expm
evolution
expm(A, *, modality=None) -> Tensor

Full matrix exponential exp(A). Use when you need the operator itself (e.g. to feed apply_linear later); use expv when you only need exp(A)·v.


time_evolve
evolution
time_evolve(H, state, t, *, hermitian=True, sparse=False, precision=1e-6, modality=None) -> Tensor

Quantum time evolution: |\u03C8(t)\u27E9 = exp(-iHt)|\u03C8(0)\u27E9. Specialized for Hermitian Hamiltonians with automatic sub-stepping.


eigs
evolution
eigs(A, *, k=1, which='smallest', hermitian=False, precision=1e-6, modality=None) -> (eigenvalues, eigenvectors)

Compute the k leading eigenpairs: A|v_k\u27E9 = \u03BB_k|v_k\u27E9. Used for spectral analysis and diagonalization.


Observable Primitives (2)

expect
observables
expect(op, state, *, shots=None, target_error=None, max_shots=None, stochastic_ok=False, modality=None) -> Tensor

Expectation value \u27E8state|op|state\u27E9. Primary measurement primitive for extracting physical quantities.


sample
observables
sample(op, state, *, n_samples, observable_basis=None, modality=None) -> Tensor (i64)

Draw n_samples measurement outcomes from the probability distribution defined by the observable and state.


State Geometry Primitives (3)

overlap
state geometry
overlap(state1, state2, *, modality=None) -> Tensor (scalar)

Inner product \u27E8state1|state2\u27E9. Possibly complex.


fidelity
state geometry
fidelity(state1, state2, *, modality=None) -> Tensor (real scalar)

State fidelity F = |\u27E8state1|state2\u27E9|\u00B2 \u2208 [0,1]. 1.0 means identical states.


variance_op
state geometry
variance_op(op, state, *, modality=None) -> Tensor (real scalar)

Observable variance: Var(O) = \u27E8O\u00B2\u27E9 - \u27E8O\u27E9\u00B2. Quantifies measurement uncertainty.


Solver Primitives (3)

linear_solve
solvers
linear_solve(A, b, *, hermitian=False, positive_definite=False, sparse=False, precision=1e-6, modality=None) -> Tensor

Solve Ax = b for x. Fundamental for SCF iterations and constrained optimization.


eigensolve
solvers
eigensolve(operand, *, k=None, result_type=None, modality=None) -> Tensor

Compute leading eigenvalues only (no eigenvectors). Lightweight alternative to eigs.


optimize
solvers
optimize(init, *, method='auto', nonconvex=False, budget=None, modality=None) -> Tensor

Variational optimization of a parameterized cost function. Cornerstone of VQE, QAOA, and quantum ML.


Norm Primitives (2)

norm
norm
norm(operand, *, result_type, axis=None, ord=2, modality=None) -> Tensor

Compute the Lp norm of a tensor along an axis.


normalize
norm
normalize(operand, *, result_type, axis=None, ord=2, modality=None) -> Tensor

Normalize a tensor: operand / norm(operand). Essential for state preparation.


Reduction Primitives (5)

reduce_sum
reduction
reduce_sum(operand, *, result_type, axis=0, modality=None) -> Tensor

Sum reduction along an axis.


reduce_mean
reduction
reduce_mean(operand, *, result_type, axis=0, modality=None) -> Tensor

Mean reduction along an axis.


reduce_max
reduction
reduce_max(operand, *, result_type, axis=0, modality=None) -> Tensor

Max reduction along an axis.


reduce_min
reduction
reduce_min(operand, *, result_type, axis=0, modality=None) -> Tensor

Min reduction along an axis.


variance
reduction
variance(operand, *, result_type, axis=0, unbiased=False, modality=None) -> Tensor

Statistical variance along an axis. Supports biased and unbiased estimates.


Soft Math Primitives (3)

clip
soft math
clip(operand, min_val, max_val, *, result_type=None, modality=None) -> Tensor

Clamp values to [min_val, max_val].


softmax
soft math
softmax(operand, *, axis=-1, modality=None) -> Tensor

Numerically stable softmax: exp(x - max(x)) / sum(exp(x - max(x))).


logsumexp
soft math
logsumexp(operand, *, result_type, axis=-1, modality=None) -> Tensor

Numerically stable log-sum-exp: log(sum(exp(x - max(x)))) + max(x).


Linear Algebra Factorizations (5)

svd
linalg
svd(A, *, full_matrices=False, modality=None) -> (U, S, Vh)

Singular value decomposition: A = U \u00b7 diag(S) \u00b7 V\u02b0. Foundation of pseudoinverse, PCA, low-rank approximation, and stable least-squares.


qr
linalg
qr(A, *, mode='reduced', modality=None) -> (Q, R)

QR factorization A = Q \u00b7 R with Q orthonormal and R upper-triangular. Used in stable least-squares, Gram-Schmidt orthogonalization, and Krylov methods.


lu
linalg
lu(A, *, modality=None) -> (P, L, U)

LU factorization with partial pivoting: P \u00b7 A = L \u00b7 U. Backbone of dense linear solves and determinant computation.


lstsq
linalg
lstsq(A, b, *, rcond=None, modality=None) -> x

Least-squares solver: minimize \u2016A\u00b7x \u2212 b\u2016\u2082. Handles overdetermined and underdetermined systems via SVD with rank truncation.


matfun
linalg
matfun(A, fn, *, modality=None) -> Tensor

Matrix function f(A) where fn \u2208 {sqrtm, logm, signm, cosm, sinm, absm}. Built on eigendecomposition or contour integration depending on the function.


FFT Family (4)

fft
fft
fft(x, *, axis=-1, n=None, modality=None) -> Tensor (complex)

Forward complex-to-complex discrete Fourier transform along an axis. Cooley\u2013Tukey radix-2/4 when n is a power of two; mixed-radix Bluestein otherwise.


ifft
fft
ifft(X, *, axis=-1, n=None, modality=None) -> Tensor (complex)

Inverse complex-to-complex DFT. Identical structure to fft with reversed twiddle direction and a 1/n normalization.


rfft
fft
rfft(x, *, axis=-1, n=None, modality=None) -> Tensor (complex)

Real-to-complex FFT. Exploits conjugate symmetry of the spectrum: output has n/2+1 complex bins instead of n.


irfft
fft
irfft(X, *, axis=-1, n=None, modality=None) -> Tensor (real)

Inverse real FFT: complex half-spectrum back to a real signal of length n. Conjugate symmetry is enforced before transform.


Convolutions (3)

conv1d
conv
conv1d(input, kernel, *, stride=1, padding=0, dilation=1, groups=1, modality=None) -> Tensor

1-D convolution with optional stride/padding/dilation/groups. Core building block for signal processing and time-series ML models.


conv2d
conv
conv2d(input, kernel, *, stride=(1,1), padding=(0,0), dilation=(1,1), groups=1, modality=None) -> Tensor

2-D convolution. The workhorse of CNN-style image and feature-map models.


conv_general_dilated
conv
conv_general_dilated(input, kernel, window_strides, padding, *, lhs_dilation, rhs_dilation, dimension_numbers, feature_group_count, batch_group_count, modality=None) -> Tensor

Generalized n-D convolution mirroring StableHLO's conv op. Handles transpose / dilated / grouped / depth-wise convolutions through a single op.


Neural-Net Building Blocks (9)

relu
nn
relu(x) -> Tensor

Rectified linear unit: max(x, 0). The default activation in most modern networks.


gelu
nn
gelu(x, *, approximate='tanh') -> Tensor

Gaussian-error linear unit. Approximated by 0.5\u00b7x\u00b7(1 + tanh(\u221a(2/\u03c0)\u00b7(x + 0.044715\u00b7x\u00b3))).


swish
nn
swish(x, *, beta=1.0) -> Tensor

SiLU / Swish activation: x \u00b7 \u03c3(\u03b2\u00b7x). Smooth, non-monotonic, often beats ReLU in deep models.


leaky_relu
nn
leaky_relu(x, *, negative_slope=0.01) -> Tensor

Leaky ReLU: x for x > 0, else negative_slope \u00b7 x. Keeps a small gradient flow through dead units.


log_softmax
nn
log_softmax(x, *, axis=-1) -> Tensor

Numerically stable log of softmax: x \u2212 logsumexp(x). Preferred over log(softmax(x)) for stability in cross-entropy losses.


layer_norm
nn
layer_norm(x, *, axis=-1, gamma=None, beta=None, eps=1e-5) -> Tensor

Layer normalization: (x \u2212 \u03bc) / \u221a(\u03c3\u00b2 + \u03b5), optionally rescaled by \u03b3 and shifted by \u03b2. Stabilizes deep transformers.


batch_norm
nn
batch_norm(x, *, axis, gamma=None, beta=None, running_mean=None, running_var=None, training=True, momentum=0.1, eps=1e-5) -> Tensor

Batch normalization. In training mode, statistics are computed across the batch and used to update running estimates; in eval mode, the running estimates are used directly.


dropout
nn
dropout(x, *, rate, training=True, seed=None) -> Tensor

Bernoulli dropout regularizer. In training, masks each element with probability rate and rescales by 1/(1\u2212rate); in eval mode, returns x unchanged.


cross_entropy_loss
nn
cross_entropy_loss(logits, labels, *, reduction='mean', label_smoothing=0.0) -> Tensor

Categorical cross-entropy. Fuses log-softmax with the gather over labels for numerical stability and a single-pass implementation.


Probability Distributions (3)

norm.logpdf
distributions
norm.logpdf(x, *, loc=0.0, scale=1.0) -> Tensor

Log-PDF of the Gaussian distribution: \u2212\u00bd\u00b7((x\u2212\u03bc)/\u03c3)\u00b2 \u2212 log(\u03c3) \u2212 \u00bd\u00b7log(2\u03c0). Exposed as a method on the `norm` distribution object.


bernoulli.logpmf
distributions
bernoulli.logpmf(k, *, p) -> Tensor

Log-PMF of the Bernoulli distribution: k\u00b7log(p) + (1\u2212k)\u00b7log(1\u2212p). Exposed as a method on the `bernoulli` distribution object.


categorical.logpmf
distributions
categorical.logpmf(k, *, logits=None, probs=None) -> Tensor

Log-PMF of the categorical distribution. Numerically stable form: logits[k] \u2212 logsumexp(logits). Exposed as a method on the `categorical` distribution object.

Execution Model Summary
Which execution models are available for each primitive category.

Primitive	CPU	CPU+GPU	CPU+TPU	CPU+QPU	NISQ Hybrid	FTQC Hybrid
apply_linear	✓	✓	✓	✓ LCU	✓	✓
expv	✓	✓	✓	✓ Trotter	✓	✓
expm	✓	✓	✓	✓ Trotter	✓	✓
time_evolve	✓	✓	✓	✓ Trotter	✓	✓
eigs	✓	✓	✓	✓ QPE	✓	✓
expect	✓	✓	✓	✓ SWAP/Pauli	✓	✓
sample	✓	✓	✓	✓ Direct	✓	✓
overlap	✓	✓	✓	✓ SWAP	✓	✓
fidelity	✓	✓	✓	✓ SWAP	✓	✓
variance_op	✓	✓	✓	✓ Pauli	✓	✓
linear_solve	✓	✓	✓	✓ VQLS	✓	✓ HHL
optimize	✓	✓	✓	✓ VQE	✓	✓
eigensolve	✓	✓	✓	—	—	—
norm / normalize	✓	✓	✓	—	—	—
reduce_* / variance	✓	✓	✓	—	—	—
clip / softmax / logsumexp	✓	✓	✓	—	—	—
svd / qr / lu / lstsq / matfun	✓	✓	✓	—	—	—
fft / ifft	✓	✓	✓	✓ QFT / IQFT	✓	✓
rfft / irfft	✓	✓	✓	—	—	—
conv1d / conv2d / conv_general	✓	✓	✓	—	—	—
relu / gelu / swish / leaky_relu	✓	✓	✓	—	—	—
log_softmax / cross_entropy_loss	✓	✓	✓	—	—	—
layer_norm / batch_norm / dropout	✓	✓	✓	—	—	—
distribution log-pdf/pmf	✓	✓	✓	—	—	

# Kernels & Domain Blocks
Kernels are domain-specific operator-construction blocks. Each kernel is a single op in the IR; the gateway lowers it server-side into a precompiled subgraph of standard ops, cached as a hermetic artifact. Output is a flat dense matrix that downstream primitives like apply_linear, eigs, expv, and expect consume directly.

Note

All kernel opcodes carry a domain prefix — kernel_* for chemistry, grid_* for physics, graph_* for ML, and markov_chain_* / thermal_* / quantum_walk_* for optimization.
Note

CPU+QPU paths.Every kernel uses the same numerical operator construction (Obara–Saika or McMurchie–Davidson recursion, scaling-and-squaring Taylor, reflector composition, etc.) regardless of the execution model. The QPU side then either consumes the materialized matrix or, where an analytical Pauli form is known (e.g. spin_chain_hamiltonian), applies the operator directly as Trotterized quantum gates.
How kernels differ from ops and primitives
Concept	Role	Lowering
Op	Elementary IR node (add, matmul, h, cnot, …)	Maps 1:1 to a StableHLO op or a quantum-circuit primitive
Primitive	Logical linear-algebra step (apply_linear, eigs, expv, fft, …)	Expanded server-side into a subgraph of ops, with one algorithm per execution model
Kernel	Domain operator-construction block (build the matrix to feed a primitive)	Expanded server-side into a precompiled, cached subgraph of standard ops

Chemistry (9 kernels)
Continuous, Gaussian-basis operator builders for molecular electronic structure. All kernels return a flat f64[n_basis²] matrix built from contracted Gaussian primitives.


overlap
chemistry
overlap(basis_info) -> f64[n_basis²]

Atomic-orbital overlap matrix S_{μν} = ⟨χ_μ | χ_ν⟩. Built from contracted Gaussian primitives via the Obara–Saika recursion.


kinetic
chemistry
kinetic(basis_info) -> f64[n_basis²]

Kinetic-energy matrix T_{μν} = −½ ⟨χ_μ | ∇² | χ_ν⟩. Computed alongside the overlap integrals from the same primitive pairs.


nuclear
chemistry
nuclear(basis_info, atoms) -> f64[n_basis²]

Nuclear-attraction matrix V_{μν} = −Σ_A Z_A · ⟨χ_μ | 1 / |r − R_A| | χ_ν⟩. The remaining one-electron term in the core Hamiltonian.


coulomb_jk
chemistry
coulomb_jk(basis_info, density) -> (f64[n_basis²], f64[n_basis²])

Coulomb J and exchange K matrices from a density matrix. The expensive O(n_basis⁴) step of a Hartree–Fock iteration.


angular_momentum
chemistry
angular_momentum(basis_info, gauge_origin) -> f64[3·n_basis²]

Angular-momentum operator components L_x, L_y, L_z about a chosen gauge origin. Used in NMR shielding and magnetic-property pipelines.


fermi_contact
chemistry
fermi_contact(basis_info, nuclei) -> f64[n_nuc·n_basis²]

Fermi-contact (δ-function) hyperfine integrals at each nuclear position. Backbone of NMR J-coupling and ESR hyperfine pipelines.


nuclear_per_atom
chemistry
nuclear_per_atom(basis_info, atoms) -> f64[n_atoms·n_basis²]

Per-atom nuclear-attraction contributions — same one-electron integrals as nuclear, kept separated by nucleus instead of summed.


int2c2e
chemistry
int2c2e(aux_basis) -> f64[n_aux²]

Two-center, two-electron repulsion integrals over an auxiliary basis. The metric matrix of density-fitting Hartree–Fock and post-HF.


int3c2e
chemistry
int3c2e(ao_basis, aux_basis) -> f64[n_basis · n_basis · n_aux]

Three-center, two-electron repulsion integrals (μν|P). The contraction tensor in density-fitting J/K builds.


Physics (6 kernels)
Discrete vector-calculus and many-body operators on regular grids and spin chains. Grid kernels share the attribute set (nx, ny, nz, dx, dy, dz, bc) and obey Laplacian = divergence ∘ gradient by construction.


grid_laplacian
physics
grid_laplacian(nx, ny, nz, dx, dy, dz, bc) -> f64[N²]

Discrete Laplacian operator ∇² on a regular nx×ny×nz grid. The canonical input to Poisson, Helmholtz, and Schrödinger eigenvalue problems.


grid_divergence
physics
grid_divergence(nx, ny, nz, dx, dy, dz, dim, bc) -> f64[N · d·N]

Discrete divergence operator ∇· mapping a d-component vector field to a scalar field on the grid.


grid_gradient
physics
grid_gradient(nx, ny, nz, dx, dy, dz, dim, bc) -> f64[d·N · N]

Discrete gradient operator ∇ mapping a scalar field on the grid to a d-component vector field.


grid_curl
physics
grid_curl(nx, ny, nz, dx, dy, dz, bc) -> f64[3N · 3N]

Discrete curl operator ∇× on a 3-D grid. Central building block of Maxwell / fluid dynamics solvers on uniform grids.


grid_helmholtz
physics
grid_helmholtz(nx, ny, nz, dx, dy, dz, k, bc) -> f64[N²]

Helmholtz operator H = ∇² + k². Stationary scattering problems and frequency-domain wave equations.


spin_chain_hamiltonian
physics
spin_chain_hamiltonian(n_spins, model, params) -> f64[2^n · 2^n]

Hamiltonians for canonical lattice models: Ising, TFI, Heisenberg, XXZ, Hubbard, and QUBO.


ML / Graph (1 kernel)

graph_laplacian
ml
graph_laplacian(adjacency, *, variant) -> f64[N²]

Graph Laplacian L = D − A in combinatorial, symmetric-normalized, or random-walk-normalized form. Core input to graph neural networks and spectral clustering.


Optimization / Monte-Carlo (3 kernels)

markov_chain_transition
optimization
markov_chain_transition(graph_weights, *, n_nodes) -> f64[N²]

Build a Markov chain transition matrix P from weighted graph edges. Backbone of MCMC and random-walk algorithms.


thermal_state
optimization
thermal_state(H, *, beta) -> f64[N²]

Gibbs / thermal state ρ = exp(−β·H) / Z(β) for a Hamiltonian H. Used in quantum-inspired sampling and free-energy estimation.


quantum_walk_operator
optimization
quantum_walk_operator(graph_weights, *, n_nodes) -> f64[2N · 2N]

Continuous- or discrete-time quantum walk operators (coin + shift) built from a graph. Used in quantum-inspired search and optimization.

Tip

Kernels are opt-in performance: you can always build the same operator manually with ops + primitives, but going through a kernel lets the gateway reuse a cached, precompiled artifact and skip redundant decomposition work on every job.

# Hardware and Backends
The gateway selects an execution backend for each job based on the algorithm, hardware availability, and user preferences. You can override the selection with a backend= tag in runtime inputs.


Execution Backends
Backend	Tag	Hardware	Description
Compiled	backend=compiled	CPU / GPU	Classical native-code execution path. Best for linear algebra and hybrid workloads.
qsim	backend=qsim	CPU	In-process quantum circuit simulator. No gRPC. Best for small circuits (< 20 qubits).
cuQuantum	backend=cuquantum	GPU (CUDA)	NVIDIA cuStateVec/cuTensorNet GPU simulator. Requires supported NVIDIA GPU.
Auto	(default)	Any	Gateway selects the best backend for the job.

Reference Backends
Reference backends provide independent validation of uniqx results against established quantum chemistry packages. They are not execution backends.

Package	Access	Capabilities
PySCF	REST: /api/reference/pyscf	Hartree-Fock SCF, NMR shieldings, J-coupling constants
ORCA	Service: port 50053	DFT energies, NMR shieldings, molecular properties

Backend Selection
Copy
import uniqx as ux

# Automatic selection (recommended)
job_id = ux.submit(module, client=client)

# Force a specific backend via runtime inputs
job_id = ux.submit(module, client=client,
    runtime_inputs=[..., "backend=compiled"])

job_id = ux.submit(module, client=client,
    runtime_inputs=[..., "backend=qsim"])

job_id = ux.submit(module, client=client,
    runtime_inputs=[..., "backend=cuquantum"])

Backend Comparison
Dimension	Compiled	qsim	cuQuantum
First-run latency	Higher (compilation)	Low	Low
Cached latency	Low	Low	Low
Max qubits	N/A (classical)	~20	~30+
GPU required	Optional	No	Yes (NVIDIA)
gRPC services	Compiler + Runtime	None	None
Precision	f32 / f64	f64	f32 / f64

Supported Hardware
Type	Platforms	Status
x86-64 CPU	Intel Xeon, AMD EPYC	Available
ARM64 / Apple Silicon	M1–M4, Graviton	Available
NVIDIA GPU (CUDA)	A100, H100, L40S	Available
Google TPU (XLA)	v4, v5e	Preview
Note

All quantum simulation runs through qsim (CPU) or cuQuantum (GPU). Physical QPU dispatch is on the roadmap via the hypervisor orchestration layer.
Full backend reference: docs.oriqx.com/architecture/backends

# Preflight and ROI
Pre-execution analysis that scores your workload across time, cost, accuracy, and carbon before committing compute resources.


Scoring Dimensions
Dimension	Description	Units
Performance	Estimated wall-clock time	Seconds
Cost	Projected compute cost	USD
Accuracy	Predicted result fidelity	Score 0-1
Carbon	Estimated CO₂ emissions	gCO₂e

API Usage
Copy
report = client.preflight(module)

report.execution_time_estimate  # float, seconds
report.cost_estimate            # float, USD
report.accuracy_score           # float, 0.0 to 1.0
report.carbon_estimate          # float, grams CO2
report.recommended_backend      # str
report.warnings                 # list[str]

Comparing Backends
Copy
cpu_report = client.preflight(module, backends=["cpu"])
gpu_report = client.preflight(module, backends=["cuda"])
print(f"CPU: {cpu_report.execution_time_estimate:.2f}s, ${cpu_report.cost_estimate:.4f}")
print(f"GPU: {gpu_report.execution_time_estimate:.2f}s, ${gpu_report.cost_estimate:.4f}")

# Error Mitigation
Techniques that improve result fidelity on noisy quantum hardware without full fault-tolerant error correction. The platform applies these automatically when targeting NISQ hardware, or you can configure them explicitly.


Overview
Error mitigation happens at different stages of the job lifecycle. Some techniques modify the circuit before it runs on hardware, others change how shots are sampled, and others correct results after measurement. The platform orchestrates all of this transparently.

Technique	When	What it does	Circuit impact	Shot overhead	Status
Dynamical Decoupling	Pre-execution	Insert refocusing pulses during idle	Adds identity gates	None	Available
Pauli Twirling	Pre-execution	Randomize gate noise into Pauli channel	Wraps each 2Q gate with random Paulis	2-4x	Available
ZNE	During execution	Run circuit at multiple noise levels	Folds circuit (U→U·U†·U)	3-5x	Available
PEC	During execution	Sample from quasi-probability decomposition	Replaces gates with noisy alternatives	10-100x	Available
T-REx	During execution	Twirl readout bits to symmetrize noise	Adds X gates before measurement	2x	Available
Clifford Data Regression	Pre + Post	Learn correction from near-Clifford circuits	Generates training circuits	5-20x	Coming soon
Virtual Distillation	During execution	Run M copies, measure symmetrized observable	M× qubit registers + SWAP network	M× qubits	Coming soon
Tensor Network Mitigation	Post-execution	Invert noise via MPO compression	None (classical post-processing)	Moderate	Coming soon
Noise-Aware Compilation	Pre-execution	Route qubits through low-error paths	Optimized transpilation	None	Coming soon

Job Lifecycle: Where Mitigation Fits
Understanding when each technique acts on your job:


Mitigation in the job pipeline
text
Copy
Job submission → Platform pipeline:

  ┌───────────────────────────────────────────────────────────────┐
  │  1. COMPILATION (before any hardware)                       │
  │     ├─ Transpile to hardware gate set                       │
  │     ├─ Noise-Aware Routing (coming soon)                    │
  │     │   └ Read calibration data, route to low-error qubits  │
  │     ├─ Dynamical Decoupling                                 │
  │     │   └ Scan for idle slots, insert DD pulse sequences    │
  │     └─ Circuit is now hardware-ready                         │
  ├───────────────────────────────────────────────────────────────┤
  │  2. CIRCUIT VARIANTS (generate multiple circuits)           │
  │     ├─ Pauli Twirling                                       │
  │     │   └ Generate K twirled copies of the circuit           │
  │     ├─ ZNE folding                                          │
  │     │   └ Fold circuit at λ = [1, 3, 5] noise levels       │
  │     ├─ PEC sampling                                         │
  │     │   └ Sample gate replacements from quasi-probability   │
  │     └─ T-REx                                                │
  │         └ Generate twirled-readout variant of each circuit   │
  ├───────────────────────────────────────────────────────────────┤
  │  3. EXECUTION (on QPU hardware)                             │
  │     ├─ Submit all circuit variants as a batch               │
  │     ├─ Shot allocation across variants (see below)          │
  │     └─ Collect raw measurement bit-strings                  │
  ├───────────────────────────────────────────────────────────────┤
  │  4. POST-PROCESSING (classical, after QPU returns)          │
  │     ├─ T-REx: XOR-undo twirls, apply bias correction       │
  │     ├─ Twirling: average over twirl instances               │
  │     ├─ PEC: weight results by sign × γ factor              │
  │     ├─ ZNE: fit extrapolation curve, evaluate at λ=0      │
  │     └─ Return mitigated expectation value                   │
  └───────────────────────────────────────────────────────────────┘

  User sees: submit(module) → result
  Platform handles: compilation → variants → execution → post-processing

Shot Allocation and Sampling Strategies
When mitigation is enabled, the platform must distribute a shot budget across multiple circuit variants. The strategy depends on which techniques are active.


Shot allocation
text
Copy
Shot Budget Allocation:

  Given: total_shots = N (user-specified or auto-determined)

  ZNE (3 noise levels):
    ├─ λ=1: N/3 shots (original circuit)
    ├─ λ=3: N/3 shots (3× folded)
    └─ λ=5: N/3 shots (5× folded)
    Optimal: allocate more shots to lower-noise circuits
      λ=1: 50%, λ=3: 30%, λ=5: 20% (variance-weighted)

  T-REx (readout twirling):
    ├─ 50% shots: random twirl bit-strings applied
    └─ 50% shots: no twirl (calibration reference)

  Pauli Twirling (K=16 twirl instances typical):
    ├─ Each twirl instance: N/K shots
    └─ Results averaged across all K instances

  PEC (quasi-probability sampling):
    ├─ Each shot: independently sample gate replacements
    ├─ Effective shots = N / γ² (reduced by overhead factor)
    └─ Need N = γ² × N_target for desired precision

  Combined (ZNE + Twirling + T-REx):
    Total circuits = 3 (ZNE levels) × 16 (twirls) × 2 (T-REx) = 96 variants
    Shots per variant = N / 96
    Minimum practical N: ~10,000 shots

  Auto-allocation ("auto" mode):
    1. Estimate circuit noise from depth + hardware error rates
    2. Choose technique stack (see Composing section)
    3. Compute optimal shot distribution via variance minimization
    4. Set total shots = max(user_requested, minimum_for_precision)

Sampling strategies
text

T-REx (Twirled Readout Error eXtinction)
When: Applied at measurement time. X gates inserted just before the measurement layer. Post-processing happens classically after all shots return.

On the circuit: For each shot, a random bit-string t is sampled. An X gate is added to qubit q whenever t[q]=1. After measurement, the result bits are XOR'd with t to undo the twirl.


Circuit transformation
text
Copy
Original circuit (3 qubits):

  q0: ──[H]──[●]────────── M ──
            │
  q1: ─────[⊕]──[●]───── M ──
                  │
  q2: ─────────[⊕]──── M ──

With T-REx (twirl t = [1, 0, 1]):

  q0: ──[H]──[●]────────── [X] ─ M ──  → result XOR 1
            │
  q1: ─────[⊕]──[●]───── ──── M ──  → result XOR 0
                  │
  q2: ─────────[⊕]──── [X] ─ M ──  → result XOR 1

Post-processing (classical):
  raw = [1, 0, 1]  →  corrected = [1⊕1, 0⊕0, 1⊕1] = [0, 0, 0]

Calibration (run once per hardware session):
  • Prepare |0⟩^n, measure with and without X twirls
  • Extract per-qubit flip rate ε_q
  • Correction factor: 1/(1 - 2ε_q) per qubit

Accuracy gain: removes ~90% of readout error
Cost: 2× shots (half twirled, half untwirled for calibration)
Compatible with: expect, sample, overlap, fidelity (all measurement primitives)

ZNE (Zero-Noise Extrapolation)
When: Before execution, the platform generates multiple folded copies of the circuit. All variants are batched to the QPU together. Extrapolation is classical post-processing.

On the circuit:Circuit folding appends U\u2020U identity pairs. This doesn't change the ideal result but increases the effective noise because each physical gate adds error.


Circuit transformation
text
Copy
Original circuit (depth d):

  q0: ──[Ry]──[●]──────── M ──
              │
  q1: ──────[⊕]──[Rz]── M ──

λ=1 (original, depth d):
  [Ry]─[●]────────── M
        │
  ────[⊕]─[Rz]───── M

λ=3 (folded once, depth 3d):
  [Ry]─[●]─────── [●]†─[Ry]†─[Ry]─[●]──────── M
        │             │               │
  ────[⊕]─[Rz]─ [Rz]†─[⊕]†────[⊕]─[Rz]── M
          │             │
  (original U)    (U†)          (U again)
  Ideal result: identical. Noise: 3× higher.

λ=5 (folded twice, depth 5d):
  U ─ U† ─ U ─ U† ─ U ─ M
  Ideal result: identical. Noise: 5× higher.

Extrapolation (classical, after all circuits return):
  Measured: E(1)=0.72, E(3)=0.58, E(5)=0.51

  Linear:      E(0) ≈ 0.79
  Exponential: E(λ) = 0.85 - 0.13·e^{-0.3λ}  →  E(0) ≈ 0.83
  Richardson:  E(0) = w1·E(1) + w3·E(3) + w5·E(5)  ≈ 0.82

  Best fit chosen automatically by cross-validation.

Folding strategies:
  • Global folding: fold entire circuit (simplest)
  • Gate-level folding: fold individual gates (finer control)
  • Layer folding: fold circuit layer-by-layer (balanced)
  Platform default: layer folding (best noise-vs-variance tradeoff)

PEC (Probabilistic Error Cancellation)
When: Setup requires a one-time noise characterization (process tomography or randomized benchmarking). During execution, each shot uses a different randomly-sampled circuit. Post-processing weights results by sign factors.

On the circuit: For each shot, every gate in the circuit is independently replaced by a sampled noisy operation from the quasi-probability decomposition. Each shot runs a slightly different circuit.


Circuit transformation
text
Copy
Setup (one-time per hardware calibration cycle):

  For CNOT gate with depolarizing noise p=0.01:
    Ideal CNOT = 0.9934 × (noisy CNOT)
               + 0.0011 × (CNOT then X⊗I)
               + 0.0011 × (CNOT then I⊗X)
               - 0.0022 × (CNOT then X⊗X)   ← negative!
               + ...  (16 Pauli terms total)
    γ_CNOT = 1.0134 (one-norm)

Original circuit:
  q0: ─[Ry(θ)]─[●]─────── M
               │
  q1: ────────[⊕]─[Rz(φ)]─ M

Shot 1 (sampled): replace CNOT with CNOT+X⊗I, sign = +1
  q0: ─[Ry(θ)]─[●]─[X]──── M      result × (+1) × γ
               │
  q1: ────────[⊕]────[Rz(φ)]─ M

Shot 2 (sampled): keep original CNOT, sign = +1
  q0: ─[Ry(θ)]─[●]─────── M      result × (+1) × γ
               │
  q1: ────────[⊕]─[Rz(φ)]─ M

Shot 3 (sampled): replace CNOT with CNOT+X⊗X, sign = -1
  q0: ─[Ry(θ)]─[●]─[X]──── M      result × (-1) × γ
               │
  q1: ────────[⊕]─[X]─[Rz(φ)]─ M

Post-processing:
  E_mitigated = (1/N) Σ_shots sign_i × γ × measurement_i
  This is an UNBIASED estimator of the ideal expectation value.

Overhead scaling:
  γ_total = ∏_gates γ_gate
  10 CNOTs (γ=1.013 each): γ_total = 1.14 → 1.3× overhead
  50 CNOTs: γ_total = 1.92 → 3.7× overhead
  100 CNOTs: γ_total = 3.70 → 13.7× overhead
  200 CNOTs: γ_total = 13.7 → 188× overhead (practical limit)

Dynamical Decoupling
When: At compile time, before the circuit is sent to hardware. The platform analyzes the scheduled circuit for idle windows and inserts pulse sequences.

On the circuit:Identity pulse sequences (e.g., X-X or X-Y-X-Y) are inserted during time slots where a qubit is idle (waiting for another qubit's gate to finish). These pulses cancel out slow environmental noise.


Circuit transformation
text
Copy
Before DD (q1 idle during q0's gate sequence):

  q0: ─[Ry]─[Rz]─[Ry]─[●]─── M
                         │
  q1: ───────────────[⊕]── M
      |--- idle ---|

  During idle: q1 decoheres (T2 decay, 1/f noise, crosstalk)

After DD (XY-4 sequence inserted):

  q0: ─[Ry]────[Rz]────[Ry]────[●]─── M
                                      │
  q1: ─[X]─τ─[Y]─τ─[X]─τ─[Y]─τ─[⊕]─── M
      |------- DD sequence ------|

  Net effect on q1: X·Y·X·Y = I (identity)
  But noise during each τ interval is refocused!

Sequence selection (automatic):
  • Idle < 100ns: no DD (overhead not worth it)
  • Idle 100-500ns: single spin echo (X)
  • Idle 500ns-2µs: XY-4 sequence
  • Idle > 2µs: repeated XY-4 blocks

  Hardware-specific tuning:
  • Superconducting (IBM, Rigetti): XY-4, τ aligned to 4.5ns clock
  • Trapped ion (IonQ, Quantinuum): CPMG, longer τ intervals
  • Pulse timing respects hardware minimum gate spacing

Cost: zero additional shots, ~5-15% circuit depth increase
Effect: T2 improvement 2-10×, T1 improvement 1.5-3×

Pauli Twirling
When: Before execution, the platform generates K randomly-twirled copies of the circuit. All copies run on the QPU, results are averaged. This is a pre-requisite for PEC.

On the circuit: Each two-qubit gate is sandwiched between random Pauli operators that commute with it. Different twirl for each copy. Over many copies, coherent noise averages into a simpler stochastic Pauli channel.


Circuit transformation
text
Copy
Original circuit:

  q0: ──[●]── M
        │
  q1: ──[⊕]── M

Twirled copy 1 (random Pauli pair: Z⊗I before, Z⊗I after):

  q0: ─[Z]─[●]─[Z]─ M
             │
  q1: ─[I]─[⊕]─[I]─ M

  Check: Z⊗I commutes with CNOT?
  CNOT · (Z⊗I) = (Z⊗I) · CNOT  ✓
  So ideal result is unchanged.

Twirled copy 2 (random Pauli pair: I⊗X before, I⊗X after):

  q0: ─[I]─[●]─[I]─ M
             │
  q1: ─[X]─[⊕]─[X]─ M

  CNOT · (I⊗X) = (Z⊗X) · CNOT
  → compensation: P_after = Z⊗X instead of I⊗X

Twirl group for CNOT: 16 valid Pauli pairs
  {II, IX, IY, IZ, XI, XX, XY, XZ, ...} (filtered by commutation)

K = 16 copies (full twirl group) or K = 4-8 (random subset)

Post-processing:
  E_twirled = (1/K) Σ_k E(copy_k)

Effect on noise:
  Before: Λ = arbitrary CPTP map (has coherent terms)
  After:  Λ_twirled = Σ_P p_P · P(·)P  (Pauli channel)

  Coherent errors (systematic rotations) → incoherent errors (random flips)
  This makes PEC and other techniques more effective.

Typical overhead: K=16 copies × base shots / 16 per copy = same total shots
  But: need minimum ~100 shots per copy for statistics

Coming Soon
Note

The following advanced techniques are under active development and will be available in upcoming releases.
Clifford Data Regression (CDR)
When:Training phase runs before the target job. Generates near-Clifford circuits, executes them on both QPU and classical simulator, fits a correction model. Inference phase applies the learned correction to the target job's results.

On the circuit: Non-Clifford gates (T, Rz, Ry) are replaced with nearest Clifford gate (S, Z, X) to create classically-simulable training circuits. The target circuit itself is not modified.


Planned algorithm
text
Virtual Distillation
When: During execution. Requires M copies of the full circuit to run simultaneously on the same QPU, connected by a SWAP network.

On the circuit: M identical copies of the state preparation circuit are laid out on separate qubit registers. A cyclic permutation (controlled-SWAP network) connects them. Measurement of the ancilla gives the distilled expectation value.


Planned algorithm
text
Tensor Network Error Mitigation
When: Entirely post-execution. The circuit runs unmodified on the QPU. Classical post-processing inverts the noise using a tensor network representation.

On the circuit: No circuit modification. The noise channel is characterized separately (via randomized benchmarking or process tomography) and represented as an MPO. Correction is applied to the measurement outcomes classically.


Planned algorithm
text
Noise-Aware Compilation
When: At compile time, before any execution. Uses real-time hardware calibration data to optimize the circuit layout.

On the circuit: Qubit mapping, SWAP insertion, and gate scheduling are all optimized to minimize total circuit error rate. The logical circuit is the same, but the physical implementation uses the best-performing qubits and connections.


Planned algorithm
text

Composing Techniques
Mitigation techniques can be layered for maximum effect. The platform applies them in the optimal order automatically when using mitigation="auto".


Composition stack and ordering
text
Copy
Recommended composition order (innermost first):

  Layer 1 — COMPILE-TIME (no shot overhead):
    └ Noise-Aware Compilation: optimal qubit routing (coming soon)
    └ Dynamical Decoupling: suppress idle decoherence
    Applied: once, before any circuit variants are generated

  Layer 2 — NOISE SHAPING (2-4× overhead):
    └ Pauli Twirling: convert coherent → stochastic noise
    Applied: generates K circuit copies, each with different random twirl

  Layer 3 — NOISE REDUCTION (3-100× overhead):
    └ ZNE: extrapolate to zero noise (moderate accuracy)
    OR
    └ PEC: exact cancellation (highest accuracy, highest cost)
    Applied: per twirled copy, generates further variant circuits

  Layer 4 — READOUT CORRECTION (2× overhead):
    └ T-REx: fix measurement errors
    Applied: adds X-twirl variant of every circuit in the batch

  Total circuits submitted to QPU:
    DD only:              1 circuit
    DD + T-REx:           2 circuits
    DD + Twirl(K=8):      8 circuits
    DD + Twirl + ZNE(3):  24 circuits
    DD + Twirl + ZNE + T-REx: 48 circuits
    DD + Twirl + PEC + T-REx: 16 circuits (but γ²× shots each)

  "auto" mode decision tree:
    Circuit depth < 10:    DD only (noise negligible)
    Circuit depth 10-50:   DD + T-REx
    Circuit depth 50-200:  DD + Twirling + ZNE + T-REx
    Circuit depth > 200:   DD + Twirling + T-REx (ZNE ineffective)
    High-precision needed: DD + Twirling + PEC + T-REx

Usage
Copy
# Single technique
job = client.submit(module, mitigation="zne")

# Compose multiple (applied in optimal order)
job = client.submit(module, mitigation=["trex", "zne", "dd"])

# Full stack for maximum accuracy
job = client.submit(module, mitigation=["dd", "twirling", "pec", "trex"])

# Auto-select based on hardware noise profile and circuit depth
job = client.submit(module, mitigation="auto")

# Control shot budget
job = client.submit(module, mitigation="auto", shots=100_000)

# Compare mitigated vs unmitigated
raw_job = client.submit(module, mitigation=None)
mitigated_job = client.submit(module, mitigation="auto")

raw_result = client.get(raw_job.id)
mitigated_result = client.get(mitigated_job.id)
print(f"Raw:       {raw_result}")
print(f"Mitigated: {mitigated_result}")

# Inspect mitigation metadata
meta = client.get_metadata(mitigated_job.id)
print(f"Techniques applied: {meta.mitigation_stack}")
print(f"Total circuits run: {meta.circuit_count}")
print(f"Total shots used:   {meta.total_shots}")
print(f"Overhead factor:    {meta.overhead_factor:.1f}x")
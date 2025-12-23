# Docker Sandbox for Agent Execution - POC

## Current System State
- ✅ Docker 29.0.0 installed
- ✅ containerd running (modern container runtime)
- ✅ Ubuntu 24.04 LTS (Contabo server)
- ✅ Already have infrastructure to support this

## Quick Comparison

| Feature | Docker (On Contabo) | E2B Sandboxes |
|---------|-------------------|---------------|
| **Setup** | Already running ✅ | Need account + API key |
| **Cost** | FREE (owned compute) | Free tier: limited executions |
| **Isolation** | Container-level | Custom managed isolation |
| **Security** | Linux kernel namespaces | Custom hardened env |
| **Parallel agents** | Unlimited (resource-limited) | Free tier limits |
| **Untrusted code** | Safe (with seccomp) | Designed for this |
| **State persistence** | Manual cleanup needed | Automatic |
| **Resource control** | cgroup limits | Built-in limits |
| **Networking** | Custom setup | Built-in private networks |
| **Setup complexity** | Medium | Low |

## Docker Approach for Agents

### Basic Concept
```dockerfile
# Dockerfile.agent-sandbox
FROM python:3.12-slim

# Minimal, unprivileged runtime
RUN useradd -m -u 10000 agent
USER agent

# Install only what agent needs
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

WORKDIR /workspace
CMD ["python", "-m", "agent_executor"]
```

### Resource Isolation (cgroups)
```bash
# Per-agent limits
docker run \
  --memory="512m" \
  --cpus="1" \
  --pids-limit=50 \
  --read-only \
  --cap-drop=ALL \
  agent-sandbox:latest
```

### Parallel Agent Execution
```python
# Spawn N isolated containers for parallel agents
import docker

client = docker.from_env()

# Launch 5 agents in parallel, each in own container
containers = []
for i in range(5):
    container = client.containers.run(
        "agent-sandbox:latest",
        detach=True,
        environment={
            "AGENT_ID": f"agent-{i}",
            "TASK": task_data
        },
        memory="512m",
        cpus=1
    )
    containers.append(container)

# Wait for all to complete
for container in containers:
    result = container.wait()
    logs = container.logs().decode()
    print(f"{container.name}: {result}")
    container.remove()
```

## Advantages for Your Setup
1. **Free** - Already have Docker running on Contabo
2. **No external dependencies** - No E2B account needed
3. **Total control** - Can customize security profiles
4. **Unlimited parallel execution** - Only limited by server resources (16GB RAM, 8 cores based on Contabo specs)
5. **No API rate limits** - Unlike E2B free tier

## Disadvantages
1. **Manual security hardening** - Need to configure seccomp/AppArmor correctly
2. **Container escape risk** - Kernel exploits could break out (though rare with proper config)
3. **Resource overhead** - Each container adds ~50-100MB RAM baseline
4. **State cleanup** - Need explicit cleanup between runs
5. **No audit trail** - Unlike managed E2B service

## Security Profile Needed

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "defaultErrnoRet": 1,
  "archMap": [
    {
      "architecture": "SCMP_ARCH_X86_64",
      "subArchitectures": ["SCMP_ARCH_X86", "SCMP_ARCH_X32"]
    }
  ],
  "syscalls": [
    {
      "names": ["read", "write", "open", "close", "execve", "fork"],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

## Cost Analysis

### Docker Approach
- **Initial:** $0 (already running)
- **Per execution:** $0 (included in Contabo plan)
- **Resource:** 16GB RAM / 8 cores (shared with other services)
- **Parallel agents:** ~10 agents × 512MB = 5GB RAM usage

### E2B Approach
- **Free tier:** ~100 sandbox hours/month
- **At scale:** $0.10-1.00 per hour
- **Parallel agents:** Billed per sandbox
- **For heavy use:** Could easily exceed free tier

## Recommendation

**For your use case, Docker is better if:**
✅ You want unlimited parallel agents (free)
✅ You're comfortable with Linux security hardening
✅ You already have Contabo infrastructure
✅ You need to stay under budget

**E2B is better if:**
✅ You want managed security/isolation
✅ You want audit trails for untrusted code
✅ You're worried about kernel exploits
✅ You prefer to outsource infrastructure concerns

## Implementation Timeline

- **30 min:** Create agent-sandbox Dockerfile
- **30 min:** Set up seccomp security profile
- **1 hour:** Write Docker orchestration Python client
- **30 min:** Integrate with Flourisha agent delegation
- **1 hour:** Testing and refinement

**Total:** ~4 hours to production-ready Docker sandbox system

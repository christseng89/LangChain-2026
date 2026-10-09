# 本地 Docker Desktop Kubernetes 部署

前提：Docker Desktop 已启用 Kubernetes（Settings → Kubernetes → Enable），并且 `kubectl config current-context` 为 `docker-desktop`。

在 `production-api` 目录下执行：

```bash
# 1.（可选）构建并推送镜像到 Docker Hub；只使用现成镜像时可跳过。需先 docker login
docker buildx build --platform linux/amd64,linux/arm64 -t christseng89/production-api --push .

# 2. 创建 namespace，再只用 4 个密钥创建 Secret（不要直接用整个 .env，见下方注意）
kubectl apply -f k8s/namespace.yaml
grep -E '^(OPENAI_API_KEY|ANTHROPIC_API_KEY|LANGSMITH_API_KEY|HF_TOKEN)=' .env > /tmp/secret.env
kubectl create secret generic agent-api-secrets -n production-api --from-env-file=/tmp/secret.env
rm /tmp/secret.env

# 3. 部署并等待就绪
kubectl apply -k k8s/
kubectl rollout status deploy/agent-api -n production-api

# 4. 验证
kubectl get pods -n production-api
curl http://localhost:8000/health
# API 文档: http://localhost:8000/docs
```

常用命令：

```bash
kubectl logs -f deploy/agent-api -n production-api
kubectl rollout restart deploy/agent-api -n production-api   # 推送新镜像后重启（imagePullPolicy: Always 会重新拉取）
```

## 从 k8s 移除 production-api

```bash
# 1. 删除 k8s/ 中的所有资源（Deployment、Service、ConfigMap 和 namespace）
kubectl delete -k k8s/

# 2. 确认已清理（namespace 删除后，其中的 Secret 和 Pod 也一并删除）
kubectl get ns production-api        # 应显示 NotFound（Terminating 时稍等片刻）
kubectl get all -n production-api    # 应显示 No resources found 或 namespace 不存在
curl http://localhost:8000/health    # 应连接失败，说明 8000 端口已释放
```

仅想停止服务、保留配置和 Secret 时，可缩容到 0 个副本，之后改回 1 即可恢复：

```bash
kubectl scale deploy/agent-api -n production-api --replicas=0
kubectl scale deploy/agent-api -n production-api --replicas=1
```

可选：清理本机镜像缓存

```bash
docker rmi christseng89/production-api:latest
docker rmi agent-api:local   # 早期本地构建的镜像，如存在
```

注意：删除 namespace 会同时删除 `agent-api-secrets`，重新部署时需按上面第 2 步重新创建 Secret。

注意：
- Deployment 的 `envFrom` 顺序是 ConfigMap 在前、Secret 在后，同名变量以后者为准。因此 Secret 只能放密钥；若把整个 `.env` 放进去，`APP_ENV=development`、`RATE_LIMIT` 等会覆盖 `configmap.yaml` 中的生产配置，带引号的值也会原样保留引号。
- 缓存、限流和会话记忆均为进程内存，所以 `replicas` 固定为 1。
- 镜像架构需与节点一致：Docker Hub 上目前只有 `arm64` 版本，amd64 机器会报 `exec format error`，请按第 1 步构建多架构镜像。

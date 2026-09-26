# schedule / Sequence

```mermaid
sequenceDiagram
participant E as endpoint
participant Q as query
participant D as transaction
E->>D: transaction開始
loop 上限付きOCC retry / 新snapshot
alt not q.resource(connection, q.ResourceParams(id=resource_id))
E-->>E: raise DomainError('resource_not_found', 404)
end
E->>Q: bookings
D-->>E: commit成功時のみ応答
end
```

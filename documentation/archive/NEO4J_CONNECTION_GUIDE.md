# Neo4j Connection Guide - Tailscale Access

**Server**: leadingai004.contaboserver.net
**Tailscale IP**: 100.66.28.67
**Date**: 2025-11-14

---

## 🔐 Neo4j Credentials

**Username**: `neo4j`
**Password**: `riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj`

---

## 🌐 Accessing Neo4j Browser

### Step 1: Connect to Tailscale VPN
Make sure you're connected to your Tailscale VPN network.

### Step 2: Open Neo4j Browser
**URL**: https://neo4j.leadingai.info/browser/

### Step 3: Connection Settings

On the Neo4j Browser login screen, enter:

**Connect URL (Bolt Protocol)**:
```
bolt://100.66.28.67:7687
```

**OR** (alternative):
```
neo4j://100.66.28.67:7687
```

**Authentication**:
- **Username**: `neo4j`
- **Password**: `riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj`
- **Database**: `neo4j` (leave default)

### Step 4: Click "Connect"

You should now be connected to your Neo4j database!

---

## 🔧 Troubleshooting

### Issue: "WebSocket connection failed"
**Solution**: Make sure you're connected to Tailscale VPN

### Issue: "ServiceUnavailable: Connection refused"
**Solution**:
1. Check Neo4j is running: `docker ps | grep neo4j`
2. Check Tailscale status: `tailscale status`
3. Verify port: `ss -tlnp | grep 7687`

### Issue: "Authentication failed"
**Solution**:
1. Double-check password (copy/paste from this document)
2. Username is lowercase: `neo4j`
3. Try resetting from command line:
   ```bash
   docker exec local-ai-packaged-neo4j-1 cypher-shell -u neo4j -p riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj "SHOW DATABASES;"
   ```

---

## 💻 Connecting from Code/Scripts

### Python (neo4j driver)
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://100.66.28.67:7687",
    auth=("neo4j", "riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj")
)

with driver.session() as session:
    result = session.run("RETURN 'Hello Neo4j' AS message")
    print(result.single()["message"])

driver.close()
```

### JavaScript/TypeScript (neo4j-driver)
```typescript
import neo4j from 'neo4j-driver';

const driver = neo4j.driver(
  'bolt://100.66.28.67:7687',
  neo4j.auth.basic('neo4j', 'riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj')
);

const session = driver.session();
const result = await session.run('RETURN "Hello Neo4j" AS message');
console.log(result.records[0].get('message'));

await session.close();
await driver.close();
```

### Cypher Shell (Command Line)
```bash
docker exec -it local-ai-packaged-neo4j-1 cypher-shell -u neo4j -p riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj
```

---

## 📊 Useful Cypher Queries

### Show all databases
```cypher
SHOW DATABASES;
```

### Show all node labels
```cypher
CALL db.labels();
```

### Show all relationship types
```cypher
CALL db.relationshipTypes();
```

### Count all nodes
```cypher
MATCH (n) RETURN count(n);
```

### Show database stats
```cypher
CALL db.stats.retrieve('GRAPH COUNTS');
```

---

## 🔒 Security Notes

- Port 7687 (Bolt) is **only accessible via localhost/Tailscale**
- **NOT exposed to public internet** (secure by design)
- Only HTTP Browser interface (port 7474) is proxied through Traefik
- To access from outside: **Must be on Tailscale VPN**

---

## 📝 For .env Configuration

Add to your `.env` file:

```bash
# Neo4j Graph Database (Tailscale access)
NEO4J_URL="bolt://100.66.28.67:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj"
```

Or if running scripts on the server itself:
```bash
NEO4J_URL="bolt://localhost:7687"
```

---

**Last Updated**: 2025-11-14
**Status**: ✅ Working via Tailscale VPN

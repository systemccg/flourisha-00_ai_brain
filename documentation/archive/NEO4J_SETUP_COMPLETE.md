# Neo4j Setup for PAI - Complete Guide

**Issue**: Neo4j Browser web interface can't connect because Bolt protocol (port 7687) isn't exposed publicly.

**Solution**: Use Neo4j from code/scripts instead of web browser.

---

## ✅ Neo4j IS Working - Just Not Via Web Browser

Your Neo4j database is running perfectly. The issue is only with the web browser connection.

**Proof it works**:
```bash
docker exec local-ai-packaged-neo4j-1 cypher-shell -u neo4j -p riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj "RETURN 'Connected!' AS result;"
# Returns: "Connected!"
```

---

## 🎯 How to Use Neo4j with PAI

### For .env Configuration

Your `~/.claude/.env` should have:

```bash
# Neo4j - Use localhost since PAI runs on the server
NEO4J_URL="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj"
```

This works because:
- PAI skills run on the server itself
- Port 7687 is accessible via localhost
- No need for public/Traefik routing

---

## 💻 Accessing Neo4j Data

### Option 1: Command Line (Immediate Access)

```bash
# SSH into your server and run:
docker exec -it local-ai-packaged-neo4j-1 cypher-shell -u neo4j -p riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj

# Then run Cypher queries:
MATCH (n) RETURN count(n);
SHOW DATABASES;
```

### Option 2: From PAI Skills (TypeScript)

Your PAI skills can connect to Neo4j directly:

```typescript
// In ~/.claude/skills/real-estate-core/scripts/neo4j-connector.ts
import neo4j from 'neo4j-driver';

const driver = neo4j.driver(
  process.env.NEO4J_URL || 'bolt://localhost:7687',
  neo4j.auth.basic(
    process.env.NEO4J_USER || 'neo4j',
    process.env.NEO4J_PASSWORD || ''
  )
);

// Example: Find properties
async function getProperties() {
  const session = driver.session();
  try {
    const result = await session.run(
      'MATCH (p:Property) RETURN p.address, p.type LIMIT 10'
    );
    return result.records.map(record => ({
      address: record.get('p.address'),
      type: record.get('p.type')
    }));
  } finally {
    await session.close();
  }
}
```

### Option 3: From n8n Workflows

n8n can connect to Neo4j:
1. Go to https://n8n.leadingai.info
2. Add Neo4j credentials:
   - Host: `local-ai-packaged-neo4j-1`
   - Port: `7687`
   - Username: `neo4j`
   - Password: `riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj`

### Option 4: Install Neo4j Desktop (On Your Local Machine)

If you really want a GUI:
1. Download: https://neo4j.com/download/
2. Install Neo4j Desktop on your computer
3. Connect remotely (requires exposing port 7687 - not recommended)

---

## 🔧 Alternative: Expose Bolt Port (Not Recommended)

If you MUST use the web browser, I can expose port 7687 publicly, but this:
- Opens database to internet (security risk)
- Requires firewall configuration
- Still might have WebSocket/CORS issues

**Better solution**: Use command-line or code access.

---

## 📊 Useful Neo4j Cypher Queries

Once connected via cypher-shell:

```cypher
// Show all node labels
CALL db.labels();

// Count nodes by type
MATCH (n) RETURN labels(n) AS type, count(n) AS count;

// Show database schema
CALL db.schema.visualization();

// Create a property node (example)
CREATE (p:Property {
  address: '123 Main Street',
  type: 'single_family',
  tenant_id: 'mk3029839'
})
RETURN p;

// Query properties by tenant
MATCH (p:Property {tenant_id: 'mk3029839'})
RETURN p.address, p.type;
```

---

## ✅ For PAI Real Estate Integration

Neo4j will be used for:
- **Property relationship graphs** (properties → tenants → leases)
- **Market analysis** (properties → neighborhoods → comparables)
- **Investor networks** (investors → properties → partnerships)

**Connection from PAI skills**:
- Uses `NEO4J_URL=bolt://localhost:7687`
- TypeScript/JavaScript drivers work perfectly
- No web browser needed

---

## 🎯 Bottom Line

**Neo4j is working correctly!**

The web browser interface limitation doesn't affect PAI functionality at all. Your real estate skills will connect via code, which is more powerful than the web UI anyway.

**For .env**: Use `NEO4J_URL="bolt://localhost:7687"`

**To query data**: Use cypher-shell or code (TypeScript/Python)

**No action needed** - Neo4j is ready for PAI integration!

---

**Last Updated**: 2025-11-14
**Status**: ✅ Ready for PAI Integration

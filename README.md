
### Step 1: Generate Keyfile

Generate a secure keyfile that MongoDB will use for internal authentication:

```bash
openssl rand -base64 756 > mongo-keyfile
chmod 400 mongo-keyfile
```

* `mongo-keyfile`: The file containing the shared secret.
* `chmod 400`: Restricts access to the owner (required by MongoDB).

---

### Step 2: Initialize the Replica Set

Run the following command to initialize the replica set:

```bash
docker exec -it agentic_mongo_db mongosh -u root -p 1234 --authenticationDatabase admin --eval '
rs.initiate({
  _id: "rs0",
  members: [{ _id: 0, host: "localhost:27017" }]
})
'
```

* `agentic_mongo_db`: Name of the MongoDB Docker container.
* Replace `1234` with your actual MongoDB root password if different.
* This sets up a single-node replica set named `rs0`.

---

### Step 3: Verify Replica Set Status

Check whether the replica set has been successfully initialized:

```bash
docker exec -it agentic_mongo_db mongosh -u root -p 1234 --authenticationDatabase admin --eval "rs.isMaster()"
```

This should return `ismaster: true` and `setName: "rs0"` if the setup is successful.

---

### Step 4: Run the Initialization Script (Optional)

If you have an `init.sh` script to automate these steps:

```bash
chmod +x init.sh
./init.sh
```
---
# Run with this 

```
uvicorn app:app --reload --host 0.0.0.0 --port 8000

```
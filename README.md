#  Ubiwhere REST API

A RESTful API for managing road segments and speed readings, with dynamic traffic intensity classification based on configurable thresholds.

---

##  Features

-  Full CRUD for road segments and speed readings (authenticated users)
-  Dynamic update of intensity thresholds via API
-  Read-only access for anonymous users
-  Interactive API documentation with Swagger (... /api/docs)
-  Pre-created Admin user for dev

---

##  Getting Started

Clone the repository and spin up the environment using Docker:

```bash
git https://github.com/jpvMartins/ubiwhere-rest-api.git
cd ubiwhere-rest-api
docker compose up
```


---

##  EndPoints

-   /road/roads -> CRUD for roads
-   /road/velocit_reads -> CRUD for velocity_reads
-  /sensor/car/pass-by/?license_plate=AA16AA  -> Returns all plate reads from the last 24 hours for a given license plate.

---



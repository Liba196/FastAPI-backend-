docker cp add_index.sql poessa_db:/add_index.sql
docker exec -it poessa_db psql -U poessa_admin -d poessa_legal_rag -f /add_index.sql
<script context="module">
    let endpoint = "http://localhost:8000/api/routing";

    // return: {'isochrone': ..., 'd_lat': ..., 'd_lng': ...}
    export async function getIsochrone(lat1, lng1, lat2, lng2) {
        let url = `${endpoint}/${lat1}/${lng1}/${lat2}/${lng2}`;

        let response = await fetch(url, {
            method: 'GET',
        });
        let data = await response.json();

        return data;
    }
</script>
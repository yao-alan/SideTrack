<script context="module">
    let endpoint = "http://localhost:8000/api";

    // return: {'isochrone': ..., 'd_lat': ..., 'd_lng': ...}
    export async function getIsochrone(lat1, lng1, lat2, lng2) {
        let url = `${endpoint}/routing/${lat1}/${lng1}/${lat2}/${lng2}`;

        let response = await fetch(url, {
            method: 'GET',
        });
        let data = await response.json();
        console.log("DONE");

        return data;
    }

    export async function updateIsoParams(nlatblks, nlngblks, time) {
        let url = `${endpoint}/update/isochrone?nlatblks=${nlatblks}&nlngblks=${nlngblks}&time=${time}`;
        let response = await fetch(url, {
            method: 'POST',
        })
        return response.json();
    }
</script>
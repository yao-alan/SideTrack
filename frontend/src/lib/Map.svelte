<script>
    import { onMount } from 'svelte';
    import * as L from 'leaflet';
    import 'leaflet/dist/leaflet.css';

    let map;
    let markCoords = [];

    function placeMarker(e) {
        L.marker(e.latlng).addTo(map);
        markCoords.push(e.latlng);
    }

    function drawBox(lat1, lng1, lat2, lng2) {
        L.polygon([
            [lat1, lng1],
            [lat2, lng1],
            [lat2, lng2],
            [lat1, lng2],
        ], {
            stroke: false,
        }).addTo(map)
    }

    async function getRoute() {
        // url construction
        let url = 'http://localhost:8000/api/routing';
        markCoords.forEach(coord => url += `/${coord['lat']}/${coord['lng']}`);

        let response = await fetch(url, {
            method: 'GET',
        })
        let data = await response.json();

        // generate isochrone
        for (let i = 0; i < 50; i++) {
            for (let j = 0; j < 50; j++) {
                if (data["isochrone"][i][j] == true) {
                    drawBox(data["minlat"] + i*data["d_lat"], data["minlng"] + j*data["d_lng"],
                            data["minlat"] + (i+1)*data["d_lat"], data["minlng"] + (j+1)*data["d_lng"]);
                }
            }
        }
    }

    onMount(() => {
        map = L.map('mapDemo').setView([34.0522, -118.2437], 13);

        L.tileLayer('https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        }).addTo(map);

        map.on('click', e => placeMarker(e));
    });
</script>

<div id="mapDemo"></div>

<button on:click={() => getRoute()}>Generate route!</button>

<style>
    #mapDemo {
        height: 800px;
        width: 800px;
        border-radius: 2%;
    }
</style>
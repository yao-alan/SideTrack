<script>
    import { onMount } from 'svelte';
    import * as L from 'leaflet';
    import 'leaflet/dist/leaflet.css';

    import Routing, { getIsochrone } from './Routing.svelte';

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

    async function drawIsochrone() {
        let data = await getIsochrone(markCoords[0]['lat'], markCoords[0]['lng'],
                                markCoords[1]['lat'], markCoords[1]['lng']);

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

<div style="display: flex; flex-direction: row;">

    <div id="mapPrefs">
        <img src='sidetrack.svg' alt="Main logo." style="width: 15vw;"/>
        <input type=range>
        <button on:click={() => drawIsochrone()} style="position: absolute; bottom: 8vh;">
            Generate route!
        </button>
    </div>

    <div id="mapDemo"></div>

</div>

<style>
    #mapPrefs {
        background-color: #ffffff;
        height: 100vh;
        width: 20vw;
        display: flex;
        flex-direction: column;
        justify-content: left;
        align-items: center;
        position: relative;
        padding: 2vw;
    }

    button {
        width: 80%;
        height: 3vh;
        background-color: #82a8d6;
        border-radius: 10px;
        box-shadow: 0px 4px 8px #dddddd;
        border: 2px;
        transition: all 0.3s ease 0s;
        margin: 1vh;
    }

    button:hover {
        background-color: #5081BB;
        transform: translate(0px, -1px);
    }

    input[type="range"] {
        -webkit-appearance: none;
        width: 80%;
        border-radius: 10px;
        background-image: linear-gradient(#5081BB, #685bff);
        background-size: 100% 100%;
        margin: 1vh;
    }

    input[type="range"]::-webkit-slider-thumb {
        -webkit-appearance: none;
        height: 1px;
        width: 1px;
        border-radius: 50%;
        background: #ff4500;
        cursor: ew-resize;
        box-shadow: 10px 10px 5px #5081BB;
        transition: background .3s ease-in-out;
    }

    input[type=range]::-webkit-slider-runnable-track  {
        -webkit-appearance: none;
        box-shadow: 10px 10px 5px 0 #555;
        border: none;
        background: transparent;
    }

    #mapDemo {
        height: 100vh;
        width: 100%;
        border-radius: 0px;
    }
</style>
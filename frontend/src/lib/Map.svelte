<script>
    import { onMount } from 'svelte';
    import * as L from 'leaflet';
    import 'leaflet/dist/leaflet.css';

    import Routing, { getIsochrone, updateIsoParams } from './Routing.svelte';

    let yelpIcon = L.icon({
        iconUrl: '/src/assets/yelp_logos/Burst/yelp_burst.png',
        iconSize: [32, 36],
        iconAnchor: [16, 18]
    })
    let map;
    let markCoords = [];
    $: params = {
        'nlatblks': 50,
        'nlngblks': 50,
        'time'    : 3000,
    };

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
        await updateIsoParams(params.nlatblks, params.nlngblks, params.time);
        let data = await getIsochrone(markCoords[0]['lat'], markCoords[0]['lng'],
                                      markCoords[1]['lat'], markCoords[1]['lng']);

        // generate isochrone
        for (let i = 0; i < params.nlatblks; i++) {
            for (let j = 0; j < params.nlngblks; j++) {
                if (data["isochrone"][i][j] == true) {
                    drawBox(data["minlat"] + i*data["d_lat"], data["minlng"] + j*data["d_lng"],
                            data["minlat"] + (i+1)*data["d_lat"], data["minlng"] + (j+1)*data["d_lng"]);
                }
            }
        }

        // mark the yelp location
        let yelpStop = L.marker(
            [data["business"].coordinates.latitude,
             data["business"].coordinates.longitude],
            {icon: yelpIcon}
        ).addTo(map);

        let starImg = `regular_${Math.floor(data["business"].rating)}`;
        if (data["business"].rating % 1 != 0)
            starImg += "_half";
        
        let businessDesc = "";
        for (const desc of data["business"].categories)
            businessDesc += `${desc["title"]}, `

        yelpStop.bindPopup(
            `<div style="display: flex; flex-direction: column; justify-content: left; min-width: 0;">
                <p style="font-family: 'Readex Pro'; font-size: 30px; margin: 0; margin-top: 10px;"><b>${data["business"].name}</b></p>
                <p style="font-family: 'Readex Pro'; margin: 0; margin-bottom: 15px;">${businessDesc.substring(0, businessDesc.length-2)}</p>
                <div style="display: flex; flex-direction: row; align-items: center; gap: 10px; min-width: 0;">
                    <img src='/src/assets/yelp_stars/web_and_ios/regular/${starImg}.png' alt=${data["business"].rating} height=20vh>
                    <a href="${data["business"].url}"><img src='/src/assets/yelp_logos/Logo/Light/RGB/yelp_logo.png' alt="Link to business" height=25vh></a>
                </div>
                <p style="font-family: 'Readex Pro'; color: #AAAAAA; margin: 0; margin-bottom: 10px;">Based on ${data["business"].review_count} Reviews</p>
             </div>
            `
        ).openPopup();
    }

    onMount(() => {
        map = L.map('mapDemo').setView([34.0522, -118.2437], 13);

        L.tileLayer('https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 20
        }).addTo(map);

        map.on('click', e => placeMarker(e));
    });
</script>

<svelte:head>
    <link href="https://fonts.googleapis.com/css?family=Readex Pro" rel="stylesheet">
</svelte:head>

<div style="display: flex; flex-direction: row;">

    <div id="mapPrefs">
        <img src='sidetrack.svg' alt="Main logo." style="width: 15vh;"/>
        <input type=range>
        <button on:click={() => drawIsochrone()} style="position: absolute; bottom: 8vh;">
            <b>get sidetracked!</b>
        </button>
    </div>

    <div id="mapDemo"></div>

</div>

<style>
    #mapPrefs {
        background-color: #ffffff;
        height: 100vh;
        width: 20vh;
        display: flex;
        flex-direction: column;
        justify-content: left;
        align-items: center;
        position: relative;
        padding: 2vw;
    }

    b {
        font-family: 'Readex Pro';
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
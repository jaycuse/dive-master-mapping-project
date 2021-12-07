mapboxgl.accessToken = 'pk.eyJ1IjoibWlrZWhhbWlsdG9uMDAiLCJhIjoiNDVjS2puUSJ9.aLvWM5BnllUGJ0e6nwMSEg';
const REST_API_URL = 'https://api-iwls.dfo-mpo.gc.ca/api/v1/stations/{station_id}/data?time-series-code=wlp&from={start_date}T00:00:00Z&to={end_date}T00:00:00Z'
const STATION_ID = '5cebf1df3d0f4a073c4bbc19';
const dateInput = document.getElementById("tidedt");
const currentDate = new Date();
const tzoffset = currentDate.getTimezoneOffset();

var map = null
const points_layout =  {
                      'text-field': ['get','depthReadingFt'],
                      'text-variable-anchor': ['top','bottom','left','right'],
                      'text-radial-offset': 0.5,
                      'text-justify': 'auto',
                      'icon-image':['get','icon']
  }
// code from the next step will go here!
const dive_line_layer_regex = new RegExp('dive[0-9]\\-line[0-9]_layer');
const dive_line_points_regex = new RegExp('dive[0-9]\\-line[0-9]\\-points_layer');
const layers_data_files = [
"data/dive1-line1.geojson",
"data/dive1-line2.geojson",
"data/dive1-line3.geojson",
"data/dive2-line1.geojson",
"data/dive2-line2.geojson",
"data/dive2-line3.geojson",
"data/relief_line_10_0.geojson",
"data/relief_line_11_0.geojson",
"data/relief_line_12_0.geojson",
"data/relief_line_13_0.geojson",
"data/relief_line_14_0.geojson",
"data/relief_line_15_0.geojson",
"data/relief_line_1_5.geojson",
"data/relief_line_17_0.geojson",
"data/relief_line_18_0.geojson",
"data/relief_line_19_0.geojson",
"data/relief_line_21_0.geojson",
"data/relief_line_22_0.geojson",
"data/relief_line_23_0.geojson",
"data/relief_line_24_0.geojson",
"data/relief_line_3_0.geojson",
"data/relief_line_4_0.geojson",
"data/relief_line_5_0.geojson",
"data/relief_line_6_0.geojson",
"data/relief_line_7_0.geojson",
"data/relief_line_8_0.geojson",
"data/relief_line_9_0.geojson",
"data/dive1-line1-points.geojson",
"data/dive1-line2-points.geojson",
"data/dive1-line3-points.geojson",
"data/dive2-line1-points.geojson",
"data/dive2-line2-points.geojson",
"data/dive2-line3-points.geojson",
"data/points-of-interest.geojson",
"data/parking.geojson"
];
// Holds loaded geojson data loaded from file
const layer_data = {}
// Holds tide data loaded from dfo rest api
var tideData

// Initiates map, once initiated calls setup
function initiateMap() {
    // Only runs once all our files are loaded in
    if(Object.keys(layer_data).length == 34) {
        console.log("Done fetching geojson");
        //console.dir(layer_data);
        if(map === null) {
            map =new mapboxgl.Map({
              container: 'map',
              style: 'mapbox://styles/mapbox/outdoors-v11',
              center: [-67.0332, 45.1332],
              zoom: 18.5
            });
            setupMap();
        }
    }
}

// Calls dfo rest api and loads result into tideData
function updateTideData() {
   let restCallURL = formatRestCall();
   console.log("Load data for: " + restCallURL);
   fetchTideData(restCallURL)
}

// Set's up our map
function setupMap() {
     map =new mapboxgl.Map({
                  container: 'map',
                  style: 'mapbox://styles/mapbox/outdoors-v11',
                  center: [-67.0332, 45.1332],
                  zoom: 18.5
                });
     mapOnLoad();
    setupMarkers();
    setupClickOnPoint();
    mapOnIdleState();
    updateTideData();

    setupDateTimeUpdates();
    setupDatePicker()


       // console.dir(tideData);

}
// Set's up layer visibility and toggle buttons
function mapOnIdleState() {
// After the last frame rendered before the map enters an "idle" state.
map.on('idle', () => {
    // If these two layers were not added to the map, abort
    //if (!map.getLayer('contours') || !map.getLayer('museums')) {
    //return;
    //}

    // Enumerate ids of the layers.
    const toggleableLayerIds = ['points', 'lines'];

    // Set up the corresponding toggle button for each layer.
    for (const id of toggleableLayerIds) {
        // Skip layers that already have a button set up.
        if (document.getElementById(id)) {
            continue;
        }

        // Create a link.
        const link = document.createElement('a');
        link.id = id;
        link.href = '#';
        link.textContent = id;
        if(id != 'lines') { // dont activate lines layer yet
            link.className = 'active';
        }

        // Show or hide layer when the toggle is clicked.
        link.onclick = function (e) {
            const clickedLayer = this.textContent;
            e.preventDefault();
            e.stopPropagation();
            let vis = '';
            layers_data_files.forEach(data_file => {
                let name = data_file.replace('data/','').replace('.geojson','') + '_layer';
                if((clickedLayer === 'points' && dive_line_points_regex.test(name)) ||
                   (clickedLayer == 'lines' && dive_line_layer_regex.test(name))) {
                      vis = toggleLayerVis(name)
                }

            });
            if(vis === 'visible') {
                this.className = '';
             } else {
                this.className = 'active';
             }
        };
        const layers = document.getElementById('menu');
        layers.appendChild(link);
    }
    });
}

// Toggles our layer visibility
function toggleLayerVis(layer) {
    // Toggle layer visibility by changing the layout object's visibility property.
    const visibility = map.getLayoutProperty(layer,'visibility');
    if (visibility === 'visible') {
        map.setLayoutProperty(layer, 'visibility', 'none');
    } else {
        map.setLayoutProperty(
            layer,
            'visibility',
            'visible'
        );
    }
    return visibility
}

// Sets up an on click for each data point to do a popup
function setupClickOnPoint() {
    layers_data_files.forEach(data_file => {
        let name = data_file.replace('data/','').replace('.geojson','') + '_layer';
        map.on('click', name, (e) => {
            // Copy coordinates array.
            const coordinates = e.features[0].geometry.coordinates.slice();
            const note = e.features[0].properties.note
            const desc = e.features[0].properties.description
            let noteToAdd = ""
            if( typeof note !== 'undefined' && note != "N/A") {
                noteToAdd = "<br />Note: " + note;
            } else if (typeof desc !== 'undefined') {
                noteToAdd = "<br />Description: " + desc;
            }
            const description = 'Heading from ref. point ' +  e.features[0].properties.lineHeadingDeg + '°<br />Distance from ref. point: ' + e.features[0].properties.distanceToRefPtFt + ' ft.' + noteToAdd;

            // Ensure that if the map is zoomed out such that multiple
            // copies of the feature are visible, the popup appears
            // over the copy being pointed to.
            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
            }

            new mapboxgl.Popup()
            .setLngLat(coordinates)
            .setHTML(description)
            .addTo(map);
            });
        });
}

// Setup triggers to update depths as user changes date and time
function setupDateTimeUpdates() {
     // update hour filter when the slider is dragged
     document.getElementById('slider').addEventListener('input', (event) => {
        updateVisuals(dateInput.value, event.target.value)
     });

     // Update of date pick
     document.getElementById('tidedt').addEventListener('input', (event) => {
        //console.log("Datepciker on change :" + event.target.value);
        if(!dates.inRange(event.target.value, tideData[0].eventDate, tideData[tideData.length-1].eventDate)) {
            // Must update data
            fetch(formatRestCall())
                    .then(function(response) {
                      return response.json();
                    }).then(json_data => {
                        tideData = json_data;
                         updateVisuals(dateInput.value, document.getElementById('slider').value)
                    });
        } else {
            // No need to regrab data just update vis
            updateVisuals(dateInput.value,document.getElementById('slider').value);
        }

     });
}

// Updates depths to selected date and time
function updateVisuals(dateValue, timeValue) {
         let timeString = timeSliderValueToTimeString(timeValue);

         document.getElementById('active-hour').innerText = timeString;

         let tideM  = findTideHeightMeters(tideData,dateValue,timeString)
         let tideFt = tideM * 3.2808

         layers_data_files.forEach(data_file => {
             let name = data_file.replace('data/','').replace('.geojson','');

             if(name.includes('points')) {
               let points = layer_data[data_file]
               points.features.forEach(feature => {
                    realDepth = (feature.properties['depthReadingFt'] +  (tideFt - feature.properties['tideHeightFt'])).toFixed(2)
                    if(realDepth <= 0) {
                        feature.properties['depthAdjustedFt'] = 'N/A' ;
                    } else {
                        feature.properties['depthAdjustedFt'] =  realDepth + ' ft';
                    }
               });
               map.getSource(name).setData(layer_data[data_file]);
             }
         });
}

//  Converts our slider value to time string
function timeSliderValueToTimeString(value) {
    let hour = parseFloat(value);
    add0 = false;

    if(hour+1 < 10) {
        add0 = true
    }
    let min = ':00';
      if(hour % 1 == 0.5){
         min = ':30'
         hour = hour - 0.5
     }
     hour = hour + 1
     if (add0) {
        return "0"+ hour + min;
     } else {
        return hour + min;
     }
}

// Set up a marker for our reference point
function setupMarkers() {
    // add markers to map
    for (const feature of geojson.features) {
      // create a HTML element for each feature
      const el = document.createElement('div');
      el.className = 'marker';

      // make a marker for each feature and add to the map
      //new mapboxgl.Marker(el).setLngLat(feature.geometry.coordinates).addTo(map);
      new mapboxgl.Marker(el)
      .setLngLat(feature.geometry.coordinates)
      .setPopup(
        new mapboxgl.Popup({ offset: 25 }) // add popups
          .setHTML(
            `<h3>${feature.properties.title}</h3><p>${feature.properties.description}</p>`
          )
      )
      .addTo(map);
    }
}

function mapOnLoad() {
    map.on('load', () => {
                map.loadImage('./assets/anchor-ball-small.png', (error, image) => {
                    map.addImage('anchor-ball-icon', image, { 'sdf': true });
                    map.loadImage('./assets/anchor-small.png', (error, image) => {
                        map.addImage('anchor-icon', image, { 'sdf': true });
                        map.loadImage('./assets/pipe-small.png', (error, image) => {
                            map.addImage('pipe-icon', image, { 'sdf': true });
                            map.loadImage('./assets/buoy-small.png', (error, image) => {
                                map.addImage('buoy-icon', image, { 'sdf': true });
                                map.loadImage('./assets/circle-15.png', (error, image) => {
                                    map.addImage('circle-icon', image, { 'sdf': true });

                                    //Add reference point layer
                                    map.addSource('points',{ 'type': 'geojson','data': points })
                                    map.addLayer({
                                        'id': 'points-depth',
                                        'type': 'symbol',
                                        'source': 'points',
                                        'layout': {
                                                'text-variable-anchor': ['top','bottom','left','right'],
                                                'text-radial-offset': 0.5,
                                                'text-justify': 'auto',
                                                'icon-image':['get','icon']
                                                }
                                    });

                                   // Dynamically add layers for our geojson data that was loaded by file
                                   layers_data_files.forEach(data_file => {
                                        let name = data_file.replace('data/','').replace('.geojson','');
                                        // Setup layer for lines
                                        let layer = {
                                            'id': name+'_layer',
                                            'type': 'line',
                                            'source': name
                                            }
                                        if(name.includes('parking')) {
                                            layer = {
                                                'id': name+'_layer',
                                                'type': 'fill',
                                                'source': name,
                                                'paint': {
                                                    'fill-color': '#303030',
                                                    'fill-opacity': 0.5
                                                }
                                            }
                                        } else if(name.includes('points')) {
                                            // Setup layer for points
                                            layer = {
                                                'id': name+'_layer',
                                                'type': 'symbol',
                                                'source': name,
                                                'layout': {
                                                      'text-field': ['get','depthAdjustedFt'],
                                                      'text-variable-anchor': ['top','bottom','left','right'],
                                                      'text-radial-offset': 0.5,
                                                      'text-justify': 'auto',
                                                      'icon-image': ['get','icon'],
                                                      'icon-size': 0.75
                                                  },
                                                  'paint' : {
                                                    'icon-color': [
                                                      'match',
                                                      ['get','styleName'],
                                                      'rock-to-silt',
                                                      '#996300',
                                                      'sand-dollar',
                                                      '#cccc33',
                                                      'rock-to-sand',
                                                      '#cc8500',
                                                      'sand-to-silt',
                                                      '#ffa500',
                                                      'rock-line',
                                                      '#a0a0a0',
                                                      'weeds',
                                                      '#3cb371',
                                                      'default-point',
                                                      '#303030',
                                                      '#ff6347' //default color
                                                  ]}
                                                }
                                            // Update icon for points
                                            let points = layer_data[data_file]
                                            if(!name.includes('interest')) {
                                                points.features.forEach(feature => {
                                                    feature.properties['icon'] = 'circle-icon'
                                                });
                                            }

                                        }

                                        // Add source and layer
                                        map.addSource(name,{'type':'geojson', data:layer_data[data_file]});
                                        map.addLayer(layer);

                                   });

                                   // toggle off dive lines
                                    // default dive line layers off
                                    layers_data_files.forEach(data_file => {
                                       let name = data_file.replace('data/','').replace('.geojson','') + '_layer';
                                       if(dive_line_layer_regex.test(name)) {
                                             map.setLayoutProperty(name, 'visibility', 'none');
                                       }
                                    });

                                   // Update depths with todays numbers
                                   updateVisuals(dateInput.value, document.getElementById('slider').value)
                                });
                            });
                        });
                    });
                });
            });
}

// Fetches geojson data from url
function fetchGeoJsonData() {
    layers_data_files.forEach(element => {
        fetchJsonToData(element);
    });

}
// Fetches geojson data from url and initiates the map once data is loaded
function fetchJsonToData(url) {
  return fetch(url)
    .then(function(response) {
      return response.json();
    }).then(json_data => {
        layer_data[url] = json_data;
        initiateMap();
    })
}

const geojson = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [-67.03329577, 45.13321841]
      },
      properties: {
        title: 'Parking to Beach',
        description: 'Reference Point',
        depth: '0 ft'
      }
    }
  ]
};
const points = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [-67.03329577, 45.13321841]
      },
      properties: {
        title: 'Hurr We dive',
        description: 'Reference Point',
        icon: 'marker-15'
      }
    }
  ]
};



// Sets up date and time picker
// date to today
// time to nearest next half hour.
function setupDatePicker() {
   let loadBtn = document.getElementById("loadBtn");
   let today = new Date();
   let todayUtc = today.toJSON().slice(0,10);
   let nextYear = new Date();

   nextYear.setFullYear(nextYear.getFullYear() + 1)
   let nextYearUtc = nextYear.toJSON().slice(0,10);

   dateInput.setAttribute('min', todayUtc);
   dateInput.setAttribute('max', nextYearUtc);
   dateInput.setAttribute('value', todayUtc);

   let nextHalfHour = roundDateTimeUpToHalfHour(today)

   let nextRealHourPickerVal = nextHalfHour.getHours()-1 + (nextHalfHour.getMinutes() / 30 * 0.5)
    let timeString = timeSliderValueToTimeString(nextRealHourPickerVal);
    document.getElementById('slider').value = nextRealHourPickerVal;
    document.getElementById('active-hour').innerText = timeString;
}

// Fancy time math
function roundDateTimeUpToHalfHour(mdate) {
    dateTime = mdate
    dateTime.setMilliseconds(Math.round(dateTime.getMilliseconds() / 1000) * 1000);
    dateTime.setSeconds(Math.ceil(dateTime.getSeconds() / 60) * 60);
    dateTime.setMinutes(Math.ceil(dateTime.getMinutes() / 30) * 30);
    return dateTime;
}


// Fancy template replacement
function formatRestCall() {
    let pickVal = dateInput.value;
    let pickNextWeek = new Date(pickVal);
    pickNextWeek.setDate(pickNextWeek.getDate() + 7);

    return REST_API_URL.replace(/\{start_date\}/i,pickVal)
                   .replace(/\{end_date\}/i,pickNextWeek.toJSON().slice(0,10))
                   .replace(/\{station_id}/i,STATION_ID);
}

// Fetches json data and puts it in tideData var
function fetchTideData(url) {
    return fetch(url)
        .then(function(response) {
          return response.json();
        }).then(json_data => {
            tideData = json_data;
        })
}

// expect time to just be "HH:MM"
function findTideHeightMeters(data,dateString,timeString) {
    let targetStringDate= dateString + 'T' + timeString + ":00";
    console.log(targetStringDate)
    let target = new Date(targetStringDate);
    console.log(targetStringDate + " -> " + target.toISOString())
    let timeEndsRange
    let timeStartsRange
    let tide = 0
    if(data.length > 1) {
        for (var i = 0; i < data.length; i++) {
            //console.log("Testing " + target.toISOString() + " if in range between: " + data[i].eventDate + " and " + data[i+1].eventDate);
            /*let inRange = dates.inRange(target,data[i].eventDate,data[i+1].eventDate);
            if(!isNaN(inRange) && inRange) {
                console.log(targetStringDate + " is in range between: " + data[i].eventDate + " and " + data[i+1].eventDate);
                console.log(" Meters: " + data[i].value + " QC = "+ data[i].qcFlagCode)
                console.log(" Meters: " + data[i+1].value + " QC = "+ data[i+1].qcFlagCode)
            }*/
            if(dates.compare(target,data[i].eventDate) == 0) {
                //console.log(targetStringDate + " is : " + data[i].eventDate);
                //console.log(" Meters: " + data[i].value + " QC = "+ data[i].qcFlagCode)
                console.log('DATA Found is '+data[i].eventDate + ' Tide Height in Meters: ' + data[i].value)
                //console.dir(data[i])
                tide = data[i].value
            }
        }
        if(tide == 0) {
            console.dir(data)
            console.log("NOTHING FOUND")
        }
    } else if (data.length == 1) {
        console.log("TGODO LENGTH ==1")
    } else {
      console.log("UMMMMM NO DATA")
    }
    return tide

}
// dates util I grabbed from the internet
// Source: http://stackoverflow.com/questions/497790
var dates = {
    convert:function(d) {
        // Converts the date in d to a date-object. The input can be:
        //   a date object: returned without modification
        //  an array      : Interpreted as [year,month,day]. NOTE: month is 0-11.
        //   a number     : Interpreted as number of milliseconds
        //                  since 1 Jan 1970 (a timestamp)
        //   a string     : Any format supported by the javascript engine, like
        //                  "YYYY/MM/DD", "MM/DD/YYYY", "Jan 31 2009" etc.
        //  an object     : Interpreted as an object with year, month and date
        //                  attributes.  **NOTE** month is 0-11.
        return (
            d.constructor === Date ? d :
            d.constructor === Array ? new Date(d[0],d[1],d[2]) :
            d.constructor === Number ? new Date(d) :
            d.constructor === String ? new Date(d) :
            typeof d === "object" ? new Date(d.year,d.month,d.date) :
            NaN
        );
    },
    compare:function(a,b) {
        // Compare two dates (could be of any type supported by the convert
        // function above) and returns:
        //  -1 : if a < b
        //   0 : if a = b
        //   1 : if a > b
        // NaN : if a or b is an illegal date
        // NOTE: The code inside isFinite does an assignment (=).
        return (
            isFinite(a=this.convert(a).valueOf()) &&
            isFinite(b=this.convert(b).valueOf()) ?
            (a>b)-(a<b) :
            NaN
        );
    },
    inRange:function(d,start,end) {
        // Checks if date in d is between dates in start and end.
        // Returns a boolean or NaN:
        //    true  : if d is between start and end (inclusive)
        //    false : if d is before start or after end
        //    NaN   : if one or more of the dates is illegal.
        // NOTE: The code inside isFinite does an assignment (=).
       return (
            isFinite(d=this.convert(d).valueOf()) &&
            isFinite(start=this.convert(start).valueOf()) &&
            isFinite(end=this.convert(end).valueOf()) ?
            start <= d && d <= end :
            NaN
        );
    }
}
// source: https://stackoverflow.com/a/14636431
// parseISO8601String : string -> Date
// Parse an ISO-8601 date, including possible timezone,
// into a Javascript Date object.
// Test strings: parseISO8601String(x).toISOString()
// "2013-01-31T12:34"              -> "2013-01-31T12:34:00.000Z"
// "2013-01-31T12:34:56"           -> "2013-01-31T12:34:56.000Z"
// "2013-01-31T12:34:56.78"        -> "2013-01-31T12:34:56.780Z"
// "2013-01-31T12:34:56.78+0100"   -> "2013-01-31T11:34:56.780Z"
// "2013-01-31T12:34:56.78+0530"   -> "2013-01-31T07:04:56.780Z"
// "2013-01-31T12:34:56.78-0330"   -> "2013-01-31T16:04:56.780Z"
// "2013-01-31T12:34:56-0330"      -> "2013-01-31T16:04:56.000Z"
// "2013-01-31T12:34:56Z"          -> "2013-01-31T12:34:56.000Z"
function parseISO8601String(dateString) {
    var timebits = /^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2})(?::([0-9]*)(\.[0-9]*)?)?(?:([+-])([0-9]{2})([0-9]{2}))?/;
    var m = timebits.exec(dateString);
    var resultDate;
    if (m) {
        var utcdate = Date.UTC(parseInt(m[1]),
                               parseInt(m[2])-1, // months are zero-offset (!)
                               parseInt(m[3]),
                               parseInt(m[4]), parseInt(m[5]), // hh:mm
                               (m[6] && parseInt(m[6]) || 0),  // optional seconds
                               (m[7] && parseFloat(m[7])*1000) || 0); // optional fraction
        // utcdate is milliseconds since the epoch
        if (m[9] && m[10]) {
            var offsetMinutes = parseInt(m[9]) * 60 + parseInt(m[10]);
            utcdate += (m[8] === '+' ? -1 : +1) * offsetMinutes * 60000;
        }
        resultDate = new Date(utcdate);
    } else {
        resultDate = null;
    }
    return resultDate;
}


     // Attempts were made to add this guy but it's using a projection that's not supported by mapboxgl
     //https://geonb.snb.ca/image/rest/services/Elevation/DSM_Hillshade_Multi_MNT_Ombrage_Multiple/ImageServer'
    // add gnb layer: https://stackoverflow.com/questions/37100144/consume-arcgis-map-service-into-mapbox-gl-api
    // https://geonb.snb.ca/image/sdk/rest/index.html#/Export_Image/02ss00000075000000/
                    //"tiles": ['https://geonb.snb.ca/image/rest/services/Elevation/DSM_Hillshade_Multi_MNT_Ombrage_Multiple/ImageServer/exportimage?dpi=96&format=png32&layers=show%3A0&bbox=-69.0500,44.6100,-63.7800,48.0700&imageSR=EPSG:2953&size=256,256&f=image'],
                    //"tiles": ['https://geonb.snb.ca/image/rest/services/Elevation/DSM_Hillshade_Multi_MNT_Ombrage_Multiple/ImageServer/exportimage?dpi=96&format=png32&layers=show%3A0&bbox=-69.0500,44.6100,-63.7800,48.0700&bboxSR=EPSG:2953&imageSR=EPSG:2953&size=256,256&f=image'],


        /*map.addLayer({
            "id": "gnb",
            "type": "raster",
            "minzoom": 0,
            "maxzoom": 22,
            "source": {
                "type": "raster",
                    "tiles": ['https://geonb.snb.ca/image/rest/services/Elevation/DSM_Hillshade_Multi_MNT_Ombrage_Multiple/ImageServer/exportimage?dpi=96&format=png32&layers=show%3A0&bbox={bbox-epsg-3857}&bboxSR=EPSG:3857&imageSR=EPSG:3857&size=256,256&f=image'],
                "tileSize": 256
                }
            });*/
<template>
    <div>
        <div v-bind:style="arrowImg">
            <img src="@/assets/arror.jpg">
        </div>
        <p>DeviceOrientation: {{ deviceOrientationMessage }}</p> <!--テストが終わったら消す-->
        <p>Geolocation: {{ geoMessage }}</p> <!--テストが終わったら消す-->
        <p>rotatedAngle: {{ rotatedAngleMessage }}</p> <!--テストが終わったら消す-->
        <p>Distance: {{ distanceMessage }}</p>
        <button v-on:click="main" >Click me!</button>
    </div>
</template>

<script>
import LatLon from 'geodesy/latlon-ellipsoidal-vincenty.js';
export default {
    data: () => {
        return {
            opponentLatitude: 35.758893,
            opponentLongitude: 139.635203,
            myLatitude: null,
            myLongitude: null,
            arrowImg: {},
            deviceOrientationMessage: "No Data",//テストが完了したら消す。
            geoMessage: "No Data",
            distanceMessage: "No Data",
            rotatedAngleMessage: "No Data"// テストが完了したら消す。
        }
    },
        computed: {
            twoOrientation: function () {//２点間の方位角を取得する関数
                let p1 = new LatLon(this.myLatitude, this.myLongitude);
                let p2 = new LatLon(this.opponentLatitude, this.opponentLongitude);
                return p1.finalBearingTo(p2);
            }
        },
        methods: {
            getMyLocation: function (position) {//自分の位置を取得する関数
                this.myLatitude = position.coords.latitude;
                this.myLongitude =  position.coords.longitude;
                this.geoMessage = "Latitude is" + this.myLatitude + "°, Longitude is" + this.myLongitude + "°";
            },
            getGeoError: function () {//自分の位置を取得出来ない時に、エラーメッセージを表示する関数
                this.geoMessage = "Unable to retrieve your location";
            },
            getTwoDistance: function() {//2点間の距離を計測する関数
                this.distanceMessage = this.myLocation.distanceTo(this.opponentLocation) + " m";
                return;
            },
            rotateArrow: function(rotatedAngle) {//矢印を回転させる関数
                this.arrowImg = {transform: "rotate(" + rotatedAngle + "deg)"};
                return;
            },
            getRotatedAngle: function() {//矢印画像を回転させるのに、必要な角度を取得する関数
                window.addEventListener("deviceorientation", function(e) {
                    let deviceOrientation = e.webkitCompassHeading;
                    this.deviceOrientationMessage = deviceOrientation; //テストが終わったら消す
                    let rotatedAngle = this.twoOrientation - deviceOrientation;
                    this.rotatedAngleMessage = rotatedAngle + "°"; //テストが終わったら消す
                    this.rotateArrow(rotatedAngle);
                },true)
            },
            main: function() {//メインの関数
                if (!navigator.geolocation){
                    this.geoMessage = "Geolocation is not supported by your browser";
                    return;
                }else{
                    if (window.DeviceOrientationEvent || window.OrientationEvent) {
                        navigator.geolocation.getCurrentPosition(this.getMyLocation, this.getGeoError);
                        if (DeviceOrientationEvent.requestPermission) {
                            DeviceOrientationEvent.requestPermission()
                            .then(response => {
                                if (response == "granted") {
                                    this.getTwoDistance();
                                    this.getRotatedAngle();
                                    return;
                                }
                            })
                            .catch(e => {
                                console.log(e);
                                return;
                            })
                        } else {
                            this.twoDistance();
                            this.getRotatedAngle();
                            return;
                        }
                    }
                }
            },
        }
    }
</script>

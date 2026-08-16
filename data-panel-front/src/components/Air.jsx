import React from "react";
import "./air.css"

export default function Air(props) {

  const shadowColor = () => {
    var aqi = props.data.air_quality['us-epa-index']
    if (aqi < 50) return "0,0,0"
    else if (aqi < 100) return "255,255,0"
    else if (aqi < 150) return "255,126,0"
    else if (aqi < 200) return "255,0,0"
    else if (aqi < 300) return "143,63,151"
    else return "126,0,35"
  }

  return (
    <>
      {
        props.data ? 
          <div
            className="airCard"
            style={{
              boxShadow: "0 0.1rem 1rem rgba(" + shadowColor()  + ", 0.8)"
            }}
          >
            <div className="airMain">
              AQI {props.data.air_quality['us-epa-index']}
            </div>
            <hr className="airDivider"/>
            <div className="airThird">
              CO: {Math.round(props.data.air_quality.co)} ppm
            </div>
            <div className="airThird">
              NO2: {Math.round(props.data.air_quality.no2*100)/100} ppm
            </div>
            <div className="airThird">
              O3: {Math.round(props.data.air_quality.o3*100)/100} ppm
            </div>
            <div className="airThird">
              SO2: {Math.round(props.data.air_quality.so2*100)/100} ppm
            </div>
          </div>
        : <></>
      }
    </> 
  )
}
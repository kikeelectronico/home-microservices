import React from "react";
import "./power.css"

export default function Power(props) {
  return (
    <>
      {
        props.data ?
          <>
            <div
              className="powerCard"
              style={{boxShadow: "0 0.1rem 1rem rgba(" + (props.data.status.current001.brightness > 90 ? "255,0,0" : "0,0,0")  + ", 0.8)"}}
            >
              <div className="powerTemperature">
                {props.data.status.current001.brightness * 35} W
              </div>
            </div>
          </>
          : <></>
      }
    </> 
  )
}
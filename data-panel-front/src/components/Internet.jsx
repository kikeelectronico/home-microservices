import React from "react";
import "./internet.css"

export default function Internet(props) {

  return (
    <>      
      {
        !props.data.connected ?
          <>
            <div className="internetCard">
              <div className="internetFail">
                Sin conexión a Internet 
              </div>
            </div>
          </>
          : <></>
      }
    </> 
  )
}
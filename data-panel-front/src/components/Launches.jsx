import React from "react";
import "./launches.css"

export default function Launches(props) {

  const getLaunchTime = (launch) => {
    return launch.net.split("T")[1].split(":")
  }

  const getMisionName = (launch) => {
    let name = launch.name.split(" | ")[0]
    return name > 30 ? name.substring(0, 30) + "..." : name
  }

  return (
    <>
      {
        props.data ? 
          props.data.launches.map(launch => {
            return (
                  <div className="launchesCard" key={launch.name}>
                    <div className="launchesName">
                      {getMisionName(launch)}
                    </div>
                    <hr className="launchDivider"/>
                    <div className="launchesNet">
                      {getLaunchTime(launch)[0]} : {getLaunchTime(launch)[1]}
                    </div>
                  </div>
              )                
            })
          
        : <></>
      }
      
    </> 
  )
}

import React, { useState, useEffect } from "react";
import './App.css';

function App() {
  const [data, setData] = useState([])

  useEffect(() => {
    fetch('/users', {
      'methods': 'GET',
      headers:{
        "Content-Type": "applications/json"
      }
      }).then(resp => resp.json())
      .then(resp => console.log(resp))
      .catch(error => console.log(error))

  }, [])

  return (
    <div className="App">
      <h1> Database Project Group 6 </h1>
    </div>
  );
}

export default App;

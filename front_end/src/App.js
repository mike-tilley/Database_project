import logo from './logo.svg';
import React, { useState, useEffect } from "react";
import './App.css';

function App() {
  // userstate for settiing a javascript 
  // object for storing and using data 

  const [data, setdata] = useState({
    name: "",
    last: "",
    age: "",  
  });

  // Using useEffect for single rendering
  useEffect(() => {
    // Using fetch to fetch the api from 
    // flask server it will be redirected to proxy
    fetch("/",)
    .then((res) =>res.json()
    .then(res => console.log(res))
    .catch(error => console.log(error))
    // .then((data) => {
    //         // Setting a data from api
    //         setdata({
    //             name: data.name,
    //             last: data.Last,
    //             age: data.Age,
                
    //         });
    //     })
    );
}, []);



  return (
    <div className="App">
      <header className="App-header">
        <h1> React and flask</h1>
        
        {/* <p>{data.name}</p>
        <p>{data.last}</p>
        <p>{data.age}</p>  */}
      </header>
    </div>
  );
}

export default App;

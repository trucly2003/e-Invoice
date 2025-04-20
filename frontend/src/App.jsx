import {  useEffect, useState } from 'react';
import { UserContext } from './configs/context';
import ApplicationRouter from './routes/applicationRouter';
import axios from 'axios';

function App() {
  const [user, setUser] = useState(null);
  const fetchUser = async () => {
    const accessToken = localStorage.getItem("token")
    if (!user && accessToken) {
      try {
        const response = await axios.get('http://localhost:8000/api/get_self/',{
          headers: {
            Authorization: "Bearer " + accessToken
          }
        })
        setUser(response['data'])
      } catch {
        localStorage.removeItem('token')
        window.location.replace('/login')
      }
      
      }  
    }
  useEffect(() => {
    fetchUser()
  },[])
  return (
    <UserContext.Provider value={{user, setUser}}>
      <ApplicationRouter/>
    </UserContext.Provider>
  );
}

export default App;

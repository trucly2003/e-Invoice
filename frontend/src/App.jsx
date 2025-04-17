import {  useState } from 'react';
import { UserContext } from './configs/context';
import ApplicationRouter from './routes/applicationRouter';

function App() {
  const [user, setUser] = useState(null);
  return (
    <UserContext.Provider value={{user, setUser}}>
      <ApplicationRouter/>
    </UserContext.Provider>
  );
}

export default App;

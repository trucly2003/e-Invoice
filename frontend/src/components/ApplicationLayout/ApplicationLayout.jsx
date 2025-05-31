import { Link, Outlet, useLocation } from "react-router-dom";
import './ApplicationLayout.css'
import { useEffect, useState } from "react";
import Header from "../Header/Header";
import Loading from "../Loading/Loading";
export default function ApplicationLayout() {
  const tabs ={
    home: {
      name: 'Home',
      url: '/home'
    },
    input: {
      name: 'Input',
      url: '/input'
    },
    invoice: {
      name: 'E-Invoice',
      url: '/invoices'
    },
    history: {
      name: 'History',
      url: '/history'
    }
  }
  const [isLoading, setIsLoading] = useState(false)
  const location = useLocation()
  const [currentPath, setCurrentPath] = useState(location['pathname'])
  useEffect(() => {
      setCurrentPath(location['pathname'])
    }, [location])
  return (
  <div className="d-flex min-vh-100" style={{ backgroundColor: '#fff5f5' }}>
      {isLoading && <Loading/>}
      <div className="bg-danger text-white p-3" style={{ width: '200px' }}>
        <h4 className="fw-bold mb-4">E-INVOICE</h4>
        <div className="mt-5">
        <ul className="nav flex-column justify-content-evenly">
          {
            Object.keys(tabs).map((tab, index) => {
              return (<li key={index} className={["nav-item mt-4 p-2", currentPath.indexOf(tabs[tab]['url']) >= 0 ? "tab_active" : ""].join(' ')}>
                <Link className="text-decoration-none text-white p-3 user-select-none"  to={tabs[tab]['url']}>{tabs[tab]['name']}</Link>
              </li>)
            })
          }
        </ul>
        </div>
      </div>
      <div className="p-4 flex-grow-1">
          <Header/>
          <Outlet context={{
            setIsLoading: setIsLoading
          }} />
      </div>
  </div>
  )
}
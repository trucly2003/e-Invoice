import { useContext } from "react"
import { UserContext } from "../../configs/context"
import './Header.css'
export default function Header() {
    const {user, setUser} = useContext(UserContext)
    const onLogout = () => {
        localStorage.removeItem('token')
        setUser(null)
        location.href.replace('/login')
    }
    return (
    user && <div className="btn-group mb-5 d-flex justify-content-end">
    <button className="user-interface dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">{user['username']}</button>
    <ul className="dropdown-menu">
        <button onClick={onLogout} className="dropdown-item fs-6">Logout</button>
    </ul>
</div>)
}
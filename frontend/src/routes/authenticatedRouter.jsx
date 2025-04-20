import { useContext } from "react";
import { useLocation, Navigate } from "react-router-dom";
import { UserContext } from "../configs/context";

export default function AuthenticatedRoute({children}) {
    const {user} = useContext(UserContext)
    const accessToken = localStorage.getItem("token")
    let {pathname} = useLocation();
    if (accessToken && !user) {
        return <div></div>
    }
    if (!user) {
        return <Navigate to={{pathname: '/login'}} state={{from: pathname}} />;
    }
    return children;
}
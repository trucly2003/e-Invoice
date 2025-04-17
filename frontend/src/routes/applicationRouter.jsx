import Dashboard from "../pages/Dashboard/Dashboard"
import LoginForm from "../pages/LoginForm/LoginForm"

import { BrowserRouter, Routes, Route } from "react-router-dom"
import AuthenticatedRoute from "./authenticatedRouter"


export default function ApplicationRouter()  {
    return (<BrowserRouter>
        <Routes>
            <Route path="/" element={<AuthenticatedRoute>
                <Dashboard/>
            </AuthenticatedRoute>}/>
            <Route path="/login" element={<LoginForm/>}/>
        </Routes>
    </BrowserRouter>)
}

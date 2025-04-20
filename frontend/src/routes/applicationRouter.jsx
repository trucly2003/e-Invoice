
import LoginForm from "../pages/LoginForm/LoginForm"

import { BrowserRouter, Routes, Route } from "react-router-dom"
import AuthenticatedRoute from "./authenticatedRouter"
import RegisterForm from "../pages/RegisterForm/RegisterForm"
import ApplicationLayout from "../components/ApplicationLayout/ApplicationLayout"
import Home from "../pages/Home/Home"
import InvoiceInput from "../pages/InvoiceInput/InvoiceInput"
import Invoices from "../pages/Invoices/Invoices"
import History from "../pages/History/History"


export default function ApplicationRouter()  {
    return (<BrowserRouter>
        <Routes>
            <Route path="/" element={<ApplicationLayout/>}>
                <Route path="/" element={<AuthenticatedRoute>
                        <Home/>
                    </AuthenticatedRoute>}/>
                <Route path="/input" element={<AuthenticatedRoute>
                        <InvoiceInput/>
                    </AuthenticatedRoute>}/>
                <Route path="/invoices" element={<AuthenticatedRoute>
                        <Invoices/>
                    </AuthenticatedRoute>}/>
                <Route path="/history" element={<AuthenticatedRoute>
                        <History/>
                    </AuthenticatedRoute>}/>
            </Route>
            <Route path="/login" element={<LoginForm/>}/>
            <Route path="/register" element={<RegisterForm/>}/>
        </Routes>
    </BrowserRouter>)
}

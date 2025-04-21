import { BsFillXCircleFill } from "react-icons/bs";
import { FaCircleCheck } from "react-icons/fa6";

export default function CheckResult({headingMessage, details, success}) {
    return(<div className="d-flex mt-4">
            <div>{success ?<FaCircleCheck color="green" size={20}  /> : <BsFillXCircleFill color="red" size={20}/>}</div>
            <div className="ms-2">
                <p className="fw-bold m-0">{headingMessage}</p>
                <ul className="list-unstyled">
                    {details.map((message, index) => {
                        return <li className={[success ? '' : 'text-danger']} key={index}>- {message}</li>
                    })}
                </ul>
            </div>
    </div>)
}
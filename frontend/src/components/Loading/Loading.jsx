import './styles.css'
export default function Loading() {

    return <div className="d-flex justify-content-center loading align-items-center">
        <div className="spinner-border" role="status">
            <span className="sr-only"></span>
        </div>
    </div>
}
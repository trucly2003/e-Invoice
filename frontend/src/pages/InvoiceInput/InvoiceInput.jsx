import { useRef, useState } from 'react';
import './InvoiceInput.css'
import { TiDeleteOutline } from "react-icons/ti";
import { BsChevronExpand } from "react-icons/bs";
import { FiUpload } from "react-icons/fi";
import axios from 'axios';

export default function InvoiceInput() {
    const fileRef = useRef(null)
    const [uploadedFiles, setUploadedFiles] = useState([])
    const [viewFile, setViewFile] = useState(null)
    const onChangeFile = () => {
        const file = fileRef.current.files[0];
        setUploadedFiles([file])
    }
    const onRemoveFile = (removeIndex) => {
        const newSelectedFiles=  uploadedFiles.filter((file, index) => index !== removeIndex)
        fileRef.current.value = null
        setUploadedFiles(newSelectedFiles)
        setViewFile(null)
    }
    const onUpload = async () => {
        const formData = new FormData()
        formData.append('file', uploadedFiles[0])
        formData.append('file_type', 'PDF')
        try {
            const token = localStorage.getItem('token')
            const response = await axios.post('http://localhost:8000/api/upload-invoice/', formData, {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            })
            if (response['status'] === 201) {
                setUploadedFiles([])
                alert("Upload success")
            }
        } catch  {
            alert("Upload failed!!!")
        }
    }
    const onViewPdf = (index) => {
        const fileUrl = URL.createObjectURL(uploadedFiles[index])

        setViewFile(fileUrl);
    }
    const onDrop = (event) => {
        event.preventDefault();
        if (event.dataTransfer.files && event.dataTransfer.files.length > 0)
        {
            const file = event.dataTransfer.files[0]
            if (file['type'] === 'application/pdf') {
                setUploadedFiles([file])
            }
        }
    }
    const onDragOver = (event) => {
        event.preventDefault();
    }
    return(
    <div className='invoice-input'>
        <form>
            <fieldset onDrop={onDrop} onDragOver={onDragOver} className="upload_dropZone text-center mb-3 p-5">
                <div className='d-flex justify-content-center'>
                    <div className='upload-image p-3'>
                        <FiUpload size={35} color='#DC3545' />
                    </div>
                </div>
                <h4 className='fw-bolder mt-2'>Drag file</h4>
                <p className='my-3'>Or browse file</p>
                <input onChange={onChangeFile} ref={fileRef} id="upload_image_background" name="input" className="position-absolute invisible" type="file" accept="application/pdf" />
                <label className="btn btn-upload mb-3 btn-danger" htmlFor="upload_image_background">Browse file</label>
                <div className="upload_gallery d-flex flex-wrap justify-content-center gap-3 mb-0"></div>
            </fieldset>
        </form>
        <div>
            <h4 className='fw-bolder mt-2'> 
                File
            </h4>
            <div>
                <table className='table'>
                    <thead>
                        <tr>
                            <th><div className='d-flex justify-content-center'>#</div></th>
                            <th><div className='d-flex justify-content-center'>File Name</div></th>
                            <th><div className='d-flex justify-content-center'>Size</div></th>
                            <th><div className='d-flex justify-content-center'>Upload At</div></th>
                            <th><div className='d-flex justify-content-center'>View</div></th>
                            <th><div className='d-flex justify-content-center'>Remove</div></th>
                        </tr>
                    </thead>
                    <tbody>
                        {
                            uploadedFiles.map((file, index) => {
                                return (
                                    <tr key={index}>   
                                        <td><div className='d-flex justify-content-center'>{index + 1}</div></td>
                                        <td><div className='d-flex justify-content-center'>{file['name']}</div></td>
                                        <td><div className='d-flex justify-content-center'>{(file['size'] / 1024).toFixed(2)}KB</div></td>
                                        <td><div className='d-flex justify-content-center'>{new Date().toLocaleDateString('vi-VN')}</div></td>
                                        <td onClick={() => onViewPdf(index)}><div className='d-flex justify-content-center'><BsChevronExpand size={18} /></div></td>
                                        <td onClick={() => onRemoveFile(index)}><div className='d-flex justify-content-center'><TiDeleteOutline color='red' size={18}/></div></td>
                                    </tr>
                                )
                            })
                        }
                    </tbody>
                </table>
            </div>
            <div className='mt-4 d-flex justify-content-end'>
                <button className='btn btn-primary' onClick={onUpload}>Upload</button>
            </div>
        </div>
        <div className='mt-5'>
            {viewFile && <object className='file-view' data={viewFile} type='application/pdf'>
                </object>}
        </div>
    </div>)
}
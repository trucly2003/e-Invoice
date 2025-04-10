import './Dashboard.css';
import pdfIcon from '../assets/pdf-icon.png'; // nếu có icon .png



export default function Dashboard() {
  const data = [
    {
      filename: 'Invoice_424.pdf',
      template: 'INV001',
      status: true,
      created: '2024-04-22',
      confirmed: '2024-04-22',
    },
    // Thêm các dòng khác nếu muốn
  ];

  return (
    <div className="d-flex min-vh-100" style={{ backgroundColor: '#fff5f5' }}>
      {/* Sidebar */}
      <div className="bg-danger text-white p-3" style={{ width: '200px' }}>
        <h4 className="fw-bold mb-4">E-INVOICE</h4>
        <ul className="nav flex-column">
          <li className="nav-item mb-2">Home</li>
          <li className="nav-item mb-2">Input</li>
          <li className="nav-item mb-2 bg-white text-danger rounded px-2 py-1 fw-bold">E-Invoice</li>
          <li className="nav-item">History</li>
        </ul>
      </div>

      {/* Main content */}
      <div className="p-4 flex-grow-1">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h5>Files</h5>
          <input type="text" className="form-control w-25" placeholder="🔍 Quick Search" />
        </div>

        <table className="table table-bordered bg-white">
          <thead className="table-light">
            <tr>
              <th>#</th>
              <th>File Name<br /><small className="text-muted">Filter</small></th>
              <th>Template Code<br /><small className="text-muted">Filter</small></th>
              <th>Status<br /><small className="text-muted">Filter</small></th>
              <th>Created On<br /><small className="text-muted">Filter</small></th>
              <th>Confirmed<br /><small className="text-muted">Filter</small></th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, idx) => (
              <tr key={idx}>
                <td>{idx + 1}</td>
                <td>
                  <img src={pdfIcon} alt="PDF" width="20" className="me-2" />
                  {item.filename}
                </td>
                <td>{item.template}</td>
                <td>
                  <span className="text-success fs-5">✔</span>
                </td>
                <td>{item.created}</td>
                <td>{item.confirmed}</td>
                <td>
                  <button className="btn btn-danger btn-sm">Check</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="d-flex justify-content-between small text-muted">
          <div>0 of {data.length} row(s) selected.</div>
          <div>Row per page: <select><option>10</option></select> | Page 1 of 1</div>
        </div>
      </div>
    </div>
  );
}

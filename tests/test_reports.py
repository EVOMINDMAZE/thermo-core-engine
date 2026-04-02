from thermoneural.reports.generator import generate_pdf_report


def test_generate_pdf_report(tmp_path):
    data = {
        'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'temperature': [22.5, 23.0, 22.8]
    }
    analysis = {
        'mean_temp': 22.77,
        'status': 'Normal'
    }

    output_pdf = tmp_path / "test_report.pdf"

    generate_pdf_report(data, analysis, str(output_pdf))

    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0

def test_generate_pdf_report_empty_data(tmp_path):
    data = {}
    analysis = {'status': 'No data'}
    output_pdf = tmp_path / "empty_report.pdf"

    generate_pdf_report(data, analysis, str(output_pdf))

    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0

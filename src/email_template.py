def moderation_email_template(request_id: int, classification: str, confidence: float, reasoning: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background-color: #f9f9f9;
          color: #333;
          margin: 0; padding: 20px;
        }}
        .container {{
          max-width: 600px;
          margin: auto;
          background-color: #ffffff;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        h2 {{
          color: #007bff;
        }}
        .info {{
          margin-top: 20px;
          line-height: 1.5;
        }}
        .footer {{
          margin-top: 30px;
          font-size: 0.9em;
          color: #777;
          text-align: center;
        }}
        .badge {{
          display: inline-block;
          padding: 5px 10px;
          background-color: #007bff;
          color: white;
          border-radius: 12px;
          font-weight: bold;
          font-size: 0.9em;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <h2>Content Moderation Result</h2>
        <p>Dear User,</p>
        <p>Your content moderation request has been processed successfully. Below are the details:</p>
        <div class="info">
          <p><strong>Request ID:</strong> {request_id}</p>
          <p><strong>Classification:</strong> <span class="badge">{classification.capitalize()}</span></p>
          <p><strong>Confidence:</strong> {confidence:.2%}</p>
          <p><strong>Reasoning:</strong> {reasoning}</p>
        </div>
        <p>If you have any questions or need assistance, please reply to this email.</p>
        <div class="footer">
          &copy; 2025 Moderation AI Team
        </div>
      </div>
    </body>
    </html>
    """



def analytics_email_html(user, total_requests, text_counts, image_counts, last_request_at):
    def build_chart_rows(counts_by_classification):
        total = sum(counts_by_classification.values()) or 1
        colors = {
            "safe": "#2ecc71",
            "toxic": "#e74c3c",
            "spam": "#f1c40f",
            "harassment": "#9b59b6"
        }

        rows_html = ""
        for classification, count in counts_by_classification.items():
            percent = (count / total) * 100
            color = colors.get(classification, "#7f8c8d")
            rows_html += f"""
            <tr>
                <td style="padding: 8px 12px;">{classification.title()}</td>
                <td style="padding: 8px 12px; text-align: right; white-space: nowrap;">{count} ({percent:.1f}%)</td>
                <td style="width: 70%; padding: 8px 0;">
                    <div style="background-color: #ecf0f1; border-radius: 4px; height: 14px; width: 100%;">
                        <div style="background-color: {color}; height: 100%; width: {percent}%; border-radius: 4px;"></div>
                    </div>
                </td>
            </tr>
            """
        return rows_html

    text_rows = build_chart_rows(text_counts)
    image_rows = build_chart_rows(image_counts)

    return f"""
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #2c3e50; background-color: #f9f9f9; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: white; border-radius: 8px; box-shadow: 0 0 12px rgba(0,0,0,0.1); padding: 30px;">
            <h2 style="color: #34495e; margin-bottom: 10px;">📊 Moderation Analytics Summary</h2>
            <p style="font-size: 18px; font-weight: bold;">Hello <strong>{user}</strong>, here’s your latest moderation analytics report:</p>

            <p style="font-size: 16px; color: #555; margin-bottom: 30px;">
                We hope this summary helps you stay informed about the moderation activities on your content. 
                If you have any questions or need assistance, feel free to reach out anytime.
            </p>

            <p style="font-size: 20px; font-weight: 700; color: #2980b9; margin: 20px 0;">
                Total Requests: {total_requests}
            </p>
            <p style="color: #7f8c8d; font-size: 14px;">
                Last Request At: {last_request_at or 'N/A'}
            </p>

            <h3 style="color: #34495e; margin-top: 40px; margin-bottom: 10px;">📝 Text Moderation Breakdown</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tbody>
                    {text_rows}
                </tbody>
            </table>

            <h3 style="color: #34495e; margin-top: 40px; margin-bottom: 10px;">🖼️ Image Moderation Breakdown</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tbody>
                    {image_rows}
                </tbody>
            </table>

            <p style="margin-top: 40px; font-size: 14px; color: #7f8c8d;">
                Best regards,<br>
                <strong>Moderation AI Team</strong>
            </p>
        </div>
    </body>
    </html>
    """

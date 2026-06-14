def verify_mail_template(username: str, link: str):
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="format-detection" content="telephone=no, date=no, address=no, email=no">
    <meta name="x-apple-disable-message-reformatting">
</head>
<body style="width: 100% !important; min-height: 100% !important; margin: 0px !important; padding: 0px !important; font-variant-ligatures: normal; text-rendering: optimizelegibility;">
	<table style="table-layout: fixed; width: 100%; max-width: 600px;" border="0" cellspacing="0" cellpadding="0" role="presentation" align="center">
		<tbody>
			<tr>
				<td align="center" valign="top">
					<table style="width: 100%; max-width: 600px; padding: 56px 0; background-color: #1b1b1b;" border="0" cellspacing="0" cellpadding="0" role="presentation">
						<tbody>
							<tr>
								<td valign="top" style="padding: 8px 36px;">
									<div style="text-align:center;font-family:Arial,Helvetica,sans-serif;color:white;font-size:23px;line-height:140%;letter-spacing:-0.3px;font-weight:800;">Hajdentity</div>
								</td>
							</tr>
						</tbody>
					</table>
					<table style="width: 100%; max-width: 600px;" border="0" cellspacing="0" cellpadding="0" role="presentation">
						<tbody>
							<tr>
								<td valign="top" align="left" style="padding: 40px; word-break: break-word; overflow-wrap: break-word;">
									<div style="text-align:left;font-family:Arial,Helvetica,sans-serif;font-weight:800;font-size:36px;line-height:128%;letter-spacing:-0.6px;padding-bottom:16px;color:#52c7f5;">Verify your email</div>
									<div style="padding-bottom:30px;">
										<div style="font-size:20px;line-height:150%;letter-spacing:-0.3px;font-family:Arial,Helvetica,sans-serif;">Hey {username},</div>
										<div style="font-size:20px;line-height:150%;letter-spacing:-0.3px;font-family:Arial,Helvetica,sans-serif;">You're almost there, just click the button below to confirm your email address and start making profiles for your beloved plushies ^-^</div>
									</div>
									<table width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="min-width:100%;">
										<tbody>
											<tr>
												<td align="center" style="padding-bottom:32px;">
													<a style="display:inline-block;border-radius:32px;background-color:#efa3b1;padding:14px 59px;font-family:Arial,Helvetica,sans-serif;color:white;font-size:16px;line-height:150%;letter-spacing:-0.3px;font-weight:500;text-decoration:none;" href="{link}" target="_blank">Verify</a>
												</td>
											</tr>
										</tbody>
									</table>
									<div style="padding-top:32px;">
										<div style="font-size:20px;line-height:150%;letter-spacing:-0.3px;font-family:Arial,Helvetica,sans-serif;">You can also copy this link:</div>
										<div style="font-size:20px;line-height:150%;letter-spacing:-0.3px;font-family:Arial,Helvetica,sans-serif;word-break:break-all;">{link}</div>
									</div>
									<div style="padding-top:30px;">
										<div style="font-size:20px;line-height:150%;letter-spacing:-0.3px;font-family:Arial,Helvetica,sans-serif;">If you didn't create an account you can safely ignore this email.</div>
										<div style="font-size:20px;line-height:150%;letter-spacing:-0.3px;font-family:Arial,Helvetica,sans-serif;">See you soon!</div>
									</div>
								</td>
							</tr>
						</tbody>
					</table>
				</td>
			</tr>
		</tbody>
	</table>
</body>
</html>
"""

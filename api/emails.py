def verify_mail_template(username: str, link: str):
    return f"""
<!DOCTYPE html>
<html>
	<head>
		<meta http-equiv="content-type" content="text/html; charset=UTF-8">
	</head>
	<body style="width: 100% !important; min-height: 100% !important; margin: 0px !important; padding: 0px !important; font-variant-ligatures: normal; text-rendering: optimizelegibility; font-feature-settings: &quot;calt&quot;;" >
		<p><br></p>
		<meta charset="UTF-8">
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<meta name="format-detection" content="telephone=no, date=no, address=no, email=no">
		<meta name="x-apple-disable-message-reformatting">
		<table style="table-layout: fixed; width: 100%; min-width: 600px;" border="0" cellspacing="0" cellpadding="0" role="presentation">
			<tbody>
				<tr>
					<td align="center" valign="top" style="width:auto;">
						<table style="width: 600px; max-width: 600px; padding: 56px 40px 56px 40px; background-color: #1b1b1b; margin-right: auto; margin-left: auto;" width="600" align="center" border="0" cellspacing="0" cellpadding="0" role="presentation">
							<tbody>
								<tr>
									<td valign="top" style="padding:  8px 36px 8px; height: unset; ">
										<div style="text-align:center;sans-serif;font-size:23px;font-family: Arial,Helvetica, sans-serif; color: white; font-size: 23px; line-height: 140%; letter-spacing: -0.3px; font-weight: 800;">Hajdentity</div>
									</td>
								</tr>
							</tbody>
						</table>
						<table style="width: 600px; max-width: 600px;" width="600" align="center" border="0" cellspacing="0" cellpadding="0" role="presentation">
							<tbody>
								<tr>
									<td valign="top" align="left"  style="padding: 40px; height: unset;">
										<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%">
											<tbody>
												<tr>
													<td valign="top" align="left">
														<div style="text-align:left;font-family:Arial, Helvetica, sans-serif; font-weight: 800; font-size: 36px; line-height: 128%; letter-spacing: -0.6px; padding-bottom: 16px; color: #52c7f5">Verify your email</div>
													</td>
												</tr>
											</tbody>
										</table>
									    <table width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation">
											<tbody>
												<tr>
													<td align="left" valign="top" style="padding: 0px 0px 30px 0px; height: auto;">
														<div style="font-size:20px;line-height:150%; letter-spacing: -0.3px;">Hey {username},</div>
														<div style="font-size:20px;line-height:150%; letter-spacing: -0.3px;">You're almost there, just click the button below to confirm your email address and start making profiles for your beloved plushies ^-^</div>
													</td>
												</tr>
											</tbody>
										</table>
										<table width="521" border="0" cellpadding="0" cellspacing="0" role="presentation" style="min-width: 100%;" height="54">
											<tbody>
												<tr>
													<th align="center" style="text-align: center; font-weight: normal;">
														<a style="display: inline-block; border-radius: 32px; background-color: #efa3b1; padding: 14px 59px 14px 59px; font-family: Arial, Helvetica, sans-serif; color: white; font-size: 16px; line-height: 150%; letter-spacing: -0.3px; font-weight: 500" href="{link}" target="_blank">Verify</a>
													</th>
												</tr>
											</tbody>
										</table>
										<table width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation">
											<tbody>
												<tr>
													<td align="left" valign="top" style="padding: 0px 0px 20px 0px; height: auto;">
														<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%">
															<tbody>
																<tr>
																	<td valign="top" align="left" style="padding: 32px 0px 0px 0px; height: auto;">
																		<div style="font-size:20px;line-height:150%; letter-spacing: -0.3px;">You can also copy this link:</div>
																		<div style="font-size:20px;line-height:150%; letter-spacing: -0.3px;">{link}</div>
																	</td>
																</tr>
															</tbody>
														</table>
													</td>
												</tr>
											</tbody>
										</table>
										<table width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation">
											<tbody>
												<tr>
													<td align="left" valign="top" style="padding: 0px 0px 30px 0px; height: auto;">
														<table border="0" cellpadding="0" cellspacing="0" width="100%">
															<tbody>
																<tr>
																	<td>
																		<div style="font-size:20px;line-height:150%; letter-spacing: -0.3px;">If you didn’t create an account you can safely ignore this email. </div>
																		<div style="font-size:20px;line-height:150%; letter-spacing: -0.3px;">See you soon!</div>
																	</td>
																</tr>
															</tbody>
														</table>
													</td>
												</tr>
											</tbody>
										</table>
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

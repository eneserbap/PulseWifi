git add .
$msg = Read-Host "Commit mesaji gir (Bos birakirsan: 'Update')"
if ($msg -eq "") { $msg = "Update" }
git commit -m "$msg"
git push origin main
write-host "Gonderildi kanka!" -ForegroundColor Green
pause
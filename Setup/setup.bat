vs_buildtools.exe --norestart --passive --wait --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.NativeDesktop --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools

cd C:\Program Files (x86)\Windows Kits\10\Lib\10*\um\x64
mklink irprops.lib bthprops.lib

pip install -r requirements.txt
pip install setuptools==57.0.0
pip install pybluez
@REM cd C:\Users\admin\Desktop\newproject\package
python setup.py sdist
pip uninstall scrapy-selenium -y
pip install ./dist/scrapy-selenium-1.0.0.tar.gz

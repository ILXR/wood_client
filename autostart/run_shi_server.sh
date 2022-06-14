WORKON_HOME=~/virtualenv
ENV=shi
cd ~/Program/wood-client
source $WORKON_HOME/$ENV/bin/activate
python ~/Program/wood-client/main.py >& log
deactivate
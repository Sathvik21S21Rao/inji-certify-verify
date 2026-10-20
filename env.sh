# source env.sh  — JDK 21 (api-test + suite need it; system java is 17) and the suite-scripts venv
export JAVA_HOME="$HOME/.local/jdks/jdk-21.0.12.1+1"
export PATH="$JAVA_HOME/bin:$PWD/.venv/bin:$PATH"

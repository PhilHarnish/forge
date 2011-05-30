echo Setup OSX
pushd config/osx
curl "https://github.com/git/git/raw/master/contrib/completion/git-completion.bash" > .git-completion.bash
cp -r ./ ~/
rm .git-completion.bash
popd

echo Install homebrew
if [ -z "$(which brew)" ]; then
  ruby -e "$(curl -fsSLk https://gist.github.com/raw/323731/install_homebrew.rb)"
fi

echo Install node
if [ -z "$(which node)" ]; then
  brew -v install --debug node
fi

echo Install npm
if [ -z "$(which npm)" ]; then
  curl http://npmjs.org/install.sh | sh
fi

# Download and update submodules.
git submodule update --init

# Update jquery submodule.
pushd third_party/jquery
git submodule update --init
if [ ! -f dist/jquery.js ]; then
  make
fi
popd


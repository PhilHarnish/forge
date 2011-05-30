# Setup OSX
pushd config/osx
curl "https://github.com/git/git/raw/master/contrib/completion/git-completion.bash" > .git-completion.bash
cp -r ./ ~/
popd

# Download and update submodules.
git submodule update --init

# Update jquery submodule.
pushd third_party/jquery
git submodule update --init
# TODO: Build a minified jquery
popd



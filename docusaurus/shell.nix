{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    nodejs
    yarn
  ];

  shellHook = ''
      export PATH="$PWD/node_modules/.bin/:$PATH"
  '';
}

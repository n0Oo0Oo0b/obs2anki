{
  description = "obs2anki";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }: utils.lib.eachDefaultSystem(system:
    let
      pkgs = import nixpkgs { inherit system; };
      python = pkgs.python312.withPackages (ps: with ps; [ ps.pyyaml ]);
      obs2anki = pkgs.writeShellApplication {
        name = "obs2anki";
        runtimeInputs = [ pkgs.ripgrep ];
        text = ''
          ${python}/bin/python ${self}/main.py "$@"
        '';
      };
    in {
      packages.obs2anki = obs2anki;
      packages.default = obs2anki;

      devShells.obs2anki = pkgs.mkShell {
        packages = [ obs2anki ];
      };
    }
  );

}

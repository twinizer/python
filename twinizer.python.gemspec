Gem::Specification.new do |spec|
  spec.name          = "twinizer-python"
  spec.version       = "0.1.0"
  spec.authors       = ["Your Name"]
  spec.email         = ["your.email@example.com"]

  spec.summary       = "A brief summary of the gem"
  spec.description   = "A detailed description of the gem"
  spec.homepage      = "https://github.com/twinizer/python"
  spec.license       = "MIT"

  spec.files         = Dir["lib/**/*.rb"]
  spec.require_paths = ["lib"]

  spec.add_dependency "jekyll", ">= 4.0"
  spec.add_dependency "faraday", ">= 1.0"
end
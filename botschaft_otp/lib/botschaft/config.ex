defmodule Botschaft.Config do
  use Agent
  alias Vapor.Provider

  def start_link(_args) do
    Agent.start_link(fn -> load() end, name: __MODULE__)
  end

  def reload() do
    Agent.update(__MODULE__, fn _ -> load() end)
  end

  def get_provider(id) when is_atom(id) do
    Agent.get(__MODULE__, fn config -> get_provider_from(config, id) end)
  end

  defp load() do
    base_env = [
      {:config_dir, "BOTSCHAFT_CONFIG_DIR", default: "./botschaft.d"}
    ]
    base_config = Vapor.load!([%Provider.Env{bindings: base_env}])

    config_file = Path.join(base_config.config_dir, "botschaft.toml")
    providers = [
      %Provider.Env{},
      %Provider.File{path: config_file, bindings: [providers: "providers", vars: "vars"]},
    ]

    # If values could not be found we raise an exception and halt the boot
    # process
    config = Vapor.load!(providers)

    config
  end

  defp get_provider_from(config, provider_id) when is_map(config) and is_atom(provider_id) do
    case Map.get(config, :providers, %{})
      |> Map.get(to_string(provider_id)) do
        %{} = dests ->
          shared_vars = get_provider_vars(config, provider_id)
          %{vars: shared_vars, destinations: dests}
        nil -> nil
      end
  end

  defp get_provider_vars(config, provider_id) when is_map(config) and is_atom(provider_id) do
    vars = Map.get(config, :vars, %{})
    globals = Map.get(vars, "global", %{})
    provider_vars = Map.get(vars, to_string(provider_id), %{})
    Map.merge(globals, provider_vars)
  end
end

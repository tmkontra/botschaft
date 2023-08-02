defmodule Botschaft.Config do
  use Agent
  alias Vapor.Provider

  defmodule ProviderConfig do
    defstruct [:destinations, :vars]

    def get_destination_config(%__MODULE__{destinations: dests}, destination_name) do
      case Map.get(dests, destination_name) do
        nil ->
          nil
        config ->
          %{"vars" => %{}}
          |> Map.merge(config)
      end
    end
  end

  def start_link(_args) do
    Agent.start_link(fn -> load() end, name: __MODULE__)
  end

  def reload() do
    Agent.update(__MODULE__, fn _ -> load() end)
  end

  def get_all_providers() do
    Agent.get(__MODULE__, fn config -> Map.get(config, :providers, %{}) end)
  end

  def get_provider_config(id) when is_atom(id) do
    Agent.get(__MODULE__, fn config -> get_provider_from(config, id) end)
  end

  def get_topics_config() do
    Agent.get(__MODULE__, fn config -> config[:topics] end)
  end

  def admin() do
    getter = fn config ->
      case Map.get(config, :admin) do
        nil -> :none
        %{} = admin_config -> {:ok, admin_config}
      end
    end
    Agent.get(__MODULE__, getter)
  end

  def auth() do
    getter = fn config ->
      auth_config = Map.get(config, :auth, %{}) || %{}
      case Map.get(auth_config, "bearer_token") do
        nil -> :not_required
        token -> {:required, token}
      end
    end
    Agent.get(__MODULE__, getter)
  end

  defp load() do
    base_env = [
      {:config_dir, "BOTSCHAFT_CONFIG_DIR", default: "./botschaft.d"},
      {:use_environment, "BOTSCHAFT_USE_ENVIRONMENT", default: false, map: &(&1 == "true")}
    ]
    base_config = Vapor.load!([%Provider.Env{bindings: base_env}])

    {:ok, config_file} = get_config_file(base_config)
    IO.puts "using config file: #{config_file}"
    providers = [
      %Provider.Env{},
      %Provider.File{
        path: config_file,
        bindings: [
          {:auth, "auth", required: false},
          {:admin, "admin", required: false},
          providers: "providers",
          vars: "vars",
          topics: "topics",
        ]
      },
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
          %ProviderConfig{vars: shared_vars, destinations: dests}
        nil -> nil
      end
  end

  defp get_provider_vars(config, provider_id) when is_map(config) and is_atom(provider_id) do
    vars = Map.get(config, :vars, %{})
    globals = Map.get(vars, "global", %{})
    provider_vars = Map.get(vars, to_string(provider_id), %{})
    Map.merge(globals, provider_vars)
  end

  # loads the config file, optionally using environment variable expansion
  # returns the config file path
  defp get_config_file(base_config) do
    config_file = Path.join(base_config.config_dir, "botschaft.toml")
    if base_config.use_environment do
      # need to envsubst and write to a temporary config file
      dir = System.tmp_dir!()
      tmp_file = Path.join(dir, "botschaft.toml")
      cmd = "envsubst < #{config_file} > #{tmp_file}"
      case System.shell(cmd, stderr_to_stdout: true) do
        {_, 0}      -> {:ok, tmp_file}
        {stdout, _} ->
          IO.puts "Failed to render environment in config file"
          IO.puts stdout
          {:error, "Cannot expand environment variables in configuration file"}
      end
    else
      {:ok, config_file}
    end
  end
end

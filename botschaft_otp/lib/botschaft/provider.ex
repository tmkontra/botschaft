defmodule Botschaft.Provider do
  defmacro __using__(name) do
    quote do
      use GenServer

      def start_link([get_provider_config]) do
        get_config = fn -> get_provider_config.(unquote(name)) end
        GenServer.start_link(__MODULE__, %{get_config: get_config}, name: __MODULE__)
      end

      def reload_config() do
        GenServer.cast(__MODULE__, :reload)
      end

      def send(destination, %Botschaft.Message{} = message) do
        GenServer.call(__MODULE__, {:message, %{destination: destination, message: message}})
      end

      def init(%{get_config: get_config} = state) do
        config = get_config.()
        {:ok, %{config: config, get_config: get_config}}
      end

      def handle_cast(:reload, %{get_config: get_config}) do
        {:noreply, %{config: get_config.(), get_config: get_config}}
      end

    end
  end
end

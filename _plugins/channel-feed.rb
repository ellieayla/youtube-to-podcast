module GenerateChannelRSS
    class ChannelRSSGenerator < Jekyll::Generator
      safe true
  
      # loop to generate each feed file
      def generate(site)
        #puts site.collections.to_yaml
        # puts "Inside generate()"
        site.collections["channels"].docs.each do |channel, posts|
          #puts channel.to_yaml
          Jekyll.logger.info "\tGenerating feed for channel: #{channel["channel_id"] }: #{channel["author"]}"
          # call to TagRSSPage instantiation function
          site.pages << ChannelRSSPage.new(site, channel, posts)
        end
      end
    end
  
    # Subclass of `Jekyll::Page` with custom method definitions.
    # TagRSSPage instantiation
    # Definition of what an RSS file looks like
    class ChannelRSSPage < Jekyll::Page
      def initialize(site, channel, posts)
        # puts "Inside initialize()"
        @site = site             # the current site instance.
        @base = site.source      # path to the source directory.
        @dir  = 'channels'    # the directory the page will reside in.
        @page = channel
        @basename = channel["channel_id"]          # filename without the extension.
        @ext      = '.xml'       # the extension.
        @name     = channel["channel_id"] + '.xml' # basically @basename + @ext
        @title = channel["author"]
        # Initialize data hash with a key pointing to all posts under current category.
        # This allows accessing the list in a template via `page.linked_docs`.
        @data = {
          'channel_id' => channel["channel_id"],
          'linked_docs' => posts,
          'content' => channel["content"],
          'channel' => channel,
          'author' => channel["author"],
          'thumbnail' => channel["thumbnail"],
          'webpage_url' => channel["webpage_url"]
          
        }
  
        # Look up front matter defaults scoped to type `channels`, if given key
        # doesn't exist in the `data` hash.
        data.default_proc = proc do |_, key|
          site.frontmatter_defaults.find(relative_path, :feedchannel, key)
        end
      end
  
      # Placeholders that are used in constructing page URL.
      def url_placeholders
        {
          :path       => @dir,
          :basename   => basename,
          :output_ext => output_ext,
        }
      end
    end
  end
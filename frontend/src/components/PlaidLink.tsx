import React, { useCallback, useState } from 'react';
import { usePlaidLink } from 'react-plaid-link';
import { useQuery, useQueryClient } from 'react-query';
import { plaidApi } from '../services/api';
import { Button } from './ui/Button';
import { LoadingSpinner } from './ui/LoadingSpinner';
import { Zap } from 'lucide-react';

interface PlaidLinkProps {
  variant?: 'primary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  children?: React.ReactNode;
}

export const PlaidLink: React.FC<PlaidLinkProps> = ({ 
  variant = 'outline', 
  size = 'sm', 
  className = '',
  children 
}) => {
  const [isConnecting, setIsConnecting] = useState(false);
  const queryClient = useQueryClient();

  // Fetch link token
  const { data: linkTokenData, isLoading: isLoadingLinkToken } = useQuery(
    'plaid-link-token',
    plaidApi.createLinkToken,
    {
      enabled: isConnecting,
      retry: 1,
    }
  );

  // Handle successful connection
  const onSuccess = useCallback(async (public_token: string, metadata: any) => {
    try {
      console.log('Plaid connection successful:', metadata);
      
      // Exchange public token for access token
      await plaidApi.exchangePublicToken({
        public_token,
        institution_id: metadata.institution.institution_id,
        institution_name: metadata.institution.name,
      });

      // Refresh plaid status and dashboard data
      queryClient.invalidateQueries('plaid-status');
      queryClient.invalidateQueries('dashboard');
      
      setIsConnecting(false);
      alert('Bank account connected successfully!');
    } catch (error) {
      console.error('Error exchanging token:', error);
      alert('Failed to connect bank account. Please try again.');
      setIsConnecting(false);
    }
  }, [queryClient]);

  // Handle errors
  const onExit = useCallback((err: any, metadata: any) => {
    console.log('Plaid Link exit:', err, metadata);
    setIsConnecting(false);
  }, []);

  // Configure Plaid Link
  const config = {
    token: linkTokenData?.link_token || null,
    onSuccess,
    onExit,
  };

  const { open, ready } = usePlaidLink(config);

  const handleConnect = () => {
    if (ready && linkTokenData?.link_token) {
      open();
    } else {
      setIsConnecting(true);
    }
  };

  const isLoading = isConnecting && isLoadingLinkToken;

  return (
    <Button
      variant={variant}
      size={size}
      className={className}
      onClick={handleConnect}
      disabled={isLoading || (isConnecting && !ready)}
    >
      {isLoading ? (
        <>
          <LoadingSpinner size="sm" className="mr-2" />
          Connecting...
        </>
      ) : (
        <>
          {children || (
            <>
              <Zap className="h-4 w-4 mr-2" />
              Connect Now
            </>
          )}
        </>
      )}
    </Button>
  );
}; 